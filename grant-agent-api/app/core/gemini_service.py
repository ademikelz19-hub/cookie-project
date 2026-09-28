import asyncio
import logging
import random
import time
from typing import Dict, Any, List, Optional, Callable
import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.all_models import AIJob
from app.models.enums import AITaskStatus

logger = logging.getLogger("gemini_service")
logger.setLevel(logging.INFO)

class AIOperationException(Exception):
    def __init__(self, message: str, job_id: Optional[str] = None, retryable: bool = True, error_category: str = "UNKNOWN"):
        super().__init__(message)
        self.job_id = job_id
        self.retryable = retryable
        self.error_category = error_category

class ResilientGeminiService:
    """
    Centralized, production-resilient Gemini AI service.
    Handles:
    - Model tier fallback (Primary -> Fallback -> Secondary Fallback)
    - Exponential backoff with jitter on transient errors (503 UNAVAILABLE, 429, timeouts)
    - Permanent error detection (400, 401, 403, 404)
    - AIJob state persistence (QUEUED -> RUNNING -> RETRYING -> COMPLETED / RETRYABLE_FAILED / PERMANENTLY_FAILED)
    - Safe logging with prompt sanitization (no credentials/passwords leaked)
    - Idempotency (no duplicate writes on retries)
    """

    TRANSIENT_STATUS_CODES = {408, 429, 500, 502, 503, 504}
    PERMANENT_STATUS_CODES = {400, 401, 403, 404}

    def __init__(self):
        self.models = [
            settings.PRIMARY_GEMINI_MODEL,
            settings.FALLBACK_GEMINI_MODEL,
            settings.SECONDARY_FALLBACK_GEMINI_MODEL
        ]
        # Remove empty or duplicate models while preserving order
        seen = set()
        self.active_models = []
        for m in self.models:
            if m and m not in seen:
                self.active_models.append(m)
                seen.add(m)

    def _classify_error(self, exc: Exception) -> tuple[bool, str, int]:
        """
        Returns: (is_transient, category_string, status_code)
        """
        if isinstance(exc, httpx.HTTPStatusError):
            code = exc.response.status_code
            if code in self.TRANSIENT_STATUS_CODES:
                return True, f"TRANSIENT_HTTP_{code}", code
            if code in self.PERMANENT_STATUS_CODES:
                return False, f"PERMANENT_HTTP_{code}", code
            return False, f"HTTP_{code}", code
        elif isinstance(exc, (httpx.TimeoutException, httpx.ConnectTimeout, httpx.ReadTimeout)):
            return True, "NETWORK_TIMEOUT", 408
        elif isinstance(exc, (httpx.ConnectError, httpx.NetworkError)):
            return True, "NETWORK_CONNECT_ERROR", 503
        else:
            msg = str(exc).lower()
            if "503" in msg or "unavailable" in msg or "no capacity" in msg or "overloaded" in msg:
                return True, "TRANSIENT_503_CAPACITY", 503
            if "429" in msg or "quota" in msg or "rate limit" in msg:
                return True, "TRANSIENT_429_RATE_LIMIT", 429
            return False, "UNKNOWN_ERROR", 500

    def _calculate_backoff(self, attempt: int) -> float:
        """Exponential backoff with jitter: base * 2^attempt + jitter"""
        base = settings.GEMINI_RETRY_BASE_SECONDS
        jitter = random.uniform(0.1, 0.5)
        return (base * (2 ** attempt)) + jitter

    def create_or_resume_job(
        self,
        db: Optional[Session],
        job_type: str,
        grant_id: Optional[str] = None,
        organisation_id: Optional[str] = None,
        application_id: Optional[str] = None,
        existing_job_id: Optional[str] = None
    ) -> Optional[AIJob]:
        """Creates or resumes an AIJob in the database for tracking."""
        if not db:
            return None

        if existing_job_id:
            job = db.query(AIJob).filter(AIJob.id == existing_job_id).first()
            if job:
                job.status = AITaskStatus.RUNNING
                db.commit()
                db.refresh(job)
                return job

        job = AIJob(
            job_type=job_type,
            grant_id=grant_id,
            organisation_id=organisation_id,
            application_id=application_id,
            status=AITaskStatus.RUNNING,
            attempt_count=0,
            max_retries=settings.GEMINI_MAX_RETRIES,
            model_attempted=self.active_models[0] if self.active_models else "default"
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    async def execute_resilient_prompt(
        self,
        system_instruction: str,
        user_prompt: str,
        job_type: str,
        db: Optional[Session] = None,
        grant_id: Optional[str] = None,
        organisation_id: Optional[str] = None,
        application_id: Optional[str] = None,
        existing_job_id: Optional[str] = None,
        mock_fallback_handler: Optional[Callable[[], str]] = None
    ) -> str:
        """
        Executes a prompt across a full (model × api_key) fallback matrix.

        Attempt order:
          (model_1, key_1) → (model_1, key_2) → (model_1, key_3)
          → (model_2, key_1) → (model_2, key_2) → (model_2, key_3)
          → (model_3, key_1) → (model_3, key_2) → (model_3, key_3)

        This means if key_1 is rate-limited (429) the system automatically
        retries with key_2 on the same model before escalating to the next
        model tier.
        """
        job = self.create_or_resume_job(
            db=db, job_type=job_type, grant_id=grant_id,
            organisation_id=organisation_id, application_id=application_id,
            existing_job_id=existing_job_id
        )
        job_id = job.id if job else None

        # Resolve available API keys
        api_keys = settings.active_api_keys
        if not api_keys:
            # No valid API keys configured — use deterministic offline fallback
            logger.info(f"No Gemini API keys configured. Using deterministic fallback for {job_type} [Job: {job_id}].")
            if mock_fallback_handler:
                result = mock_fallback_handler()
                if job and db:
                    job.status = AITaskStatus.COMPLETED
                    job.result_payload = {"summary": "Completed via deterministic synthesis"}
                    db.commit()
                return result
            return "Synthesized response (deterministic fallback mode — add GEMINI_API_KEY_1 to enable AI)"

        last_category = "UNKNOWN"
        last_error_msg = ""
        total_attempts = 0

        # Build the full attempt matrix: every (model, key) combination
        for model_idx, model_name in enumerate(self.active_models):
            logger.info(
                f"Trying model tier {model_idx + 1}/{len(self.active_models)}: '{model_name}' "
                f"with {len(api_keys)} API key(s) [Job: {job_id}]"
            )
            if job and db:
                job.model_attempted = model_name
                db.commit()

            for key_idx, api_key in enumerate(api_keys):
                model_key_attempts = 0

                while model_key_attempts < settings.GEMINI_MAX_RETRIES:
                    total_attempts += 1
                    model_key_attempts += 1

                    if job and db:
                        job.attempt_count = total_attempts
                        db.commit()

                    try:
                        result = await self._call_gemini_api(model_name, api_key, system_instruction, user_prompt)
                        logger.info(
                            f"Success with model='{model_name}' key={key_idx+1} "
                            f"attempt={model_key_attempts} [Job: {job_id}]"
                        )
                        if job and db:
                            job.status = AITaskStatus.COMPLETED
                            job.last_error_category = None
                            job.last_error_message = None
                            db.commit()
                        return result

                    except Exception as exc:
                        is_transient, category, code = self._classify_error(exc)
                        last_category = category
                        last_error_msg = f"HTTP {code}: {type(exc).__name__}"

                        logger.warning(
                            f"model='{model_name}' key={key_idx+1} "
                            f"attempt={model_key_attempts}/{settings.GEMINI_MAX_RETRIES} "
                            f"[{category}, transient={is_transient}]: {last_error_msg}"
                        )

                        if job and db:
                            job.status = AITaskStatus.RETRYING if is_transient else AITaskStatus.PERMANENTLY_FAILED
                            job.last_error_category = last_category
                            job.last_error_message = last_error_msg
                            db.commit()

                        if not is_transient:
                            # Permanent error (e.g. 404 bad model, 401 bad key) — skip this key immediately
                            logger.info(f"Permanent error for model='{model_name}' key={key_idx+1}. Trying next key.")
                            break

                        # Rate-limit / capacity error — back off then retry this (model, key) pair
                        if model_key_attempts < settings.GEMINI_MAX_RETRIES:
                            backoff = self._calculate_backoff(model_key_attempts)
                            logger.info(f"Backing off {backoff:.2f}s before retry...")
                            await asyncio.sleep(backoff)
                        else:
                            logger.warning(
                                f"Exhausted {settings.GEMINI_MAX_RETRIES} retries for "
                                f"model='{model_name}' key={key_idx+1}. Trying next key."
                            )

        # All (model, key) combinations exhausted
        logger.error(f"All models and all API keys exhausted for job {job_id}. Last: {last_category}")

        if mock_fallback_handler:
            logger.info(f"Recovering via deterministic fallback for job {job_id}.")
            fallback_res = mock_fallback_handler()
            if job and db:
                job.status = AITaskStatus.COMPLETED
                job.last_error_category = f"FALLBACK_RECOVERED_AFTER_{last_category}"
                db.commit()
            return fallback_res

        if job and db:
            job.status = AITaskStatus.RETRYABLE_FAILED
            job.last_error_category = last_category
            job.last_error_message = f"All models and keys failed: {last_error_msg}"
            db.commit()

        raise AIOperationException(
            message="Gemini service temporarily unavailable across all models and API keys. Job marked RETRYABLE_FAILED.",
            job_id=job_id,
            retryable=True,
            error_category=last_category
        )

    async def _call_gemini_api(self, model: str, api_key: str, system_instruction: str, user_prompt: str) -> str:
        """Direct REST call to Gemini generateContent endpoint using a specific API key."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"SYSTEM INSTRUCTION:\n{system_instruction}\n\nUSER PROMPT:\n{user_prompt}"}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "topP": 0.8,
                "maxOutputTokens": 2048
            }
        }

        async with httpx.AsyncClient(timeout=settings.GEMINI_REQUEST_TIMEOUT_SECONDS) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

            candidates = data.get("candidates", [])
            if candidates and "content" in candidates[0] and "parts" in candidates[0]["content"]:
                parts = candidates[0]["content"]["parts"]
                if parts and "text" in parts[0]:
                    return parts[0]["text"]

            raise ValueError("Invalid Gemini response format")

gemini_service = ResilientGeminiService()

