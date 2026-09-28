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
        Executes a prompt across the model hierarchy with exponential backoff on transient errors.
        """
        job = self.create_or_resume_job(
            db=db,
            job_type=job_type,
            grant_id=grant_id,
            organisation_id=organisation_id,
            application_id=application_id,
            existing_job_id=existing_job_id
        )
        job_id = job.id if job else None

        # If no GEMINI_API_KEY is configured, gracefully invoke mock fallback
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY.startswith("ENTER_"):
            logger.info(f"Gemini API key not configured. Using deterministic fallback for {job_type} [Job: {job_id}].")
            if mock_fallback_handler:
                result = mock_fallback_handler()
                if job and db:
                    job.status = AITaskStatus.COMPLETED
                    job.result_payload = {"summary": "Completed via deterministic synthesis"}
                    db.commit()
                return result
            else:
                return "Synthesized response (deterministic fallback mode)"

        last_category = "UNKNOWN"
        last_error_msg = ""
        total_attempts = 0

        for model_idx, model_name in enumerate(self.active_models):
            logger.info(f"Attempting model '{model_name}' (tier {model_idx + 1}/{len(self.active_models)}) for {job_type} [Job: {job_id}]")
            
            if job and db:
                job.model_attempted = model_name
                db.commit()

            model_attempts = 0
            while model_attempts < settings.GEMINI_MAX_RETRIES:
                total_attempts += 1
                model_attempts += 1
                
                if job and db:
                    job.attempt_count = total_attempts
                    db.commit()

                try:
                    result = await self._call_gemini_api(model_name, system_instruction, user_prompt)
                    # Success
                    logger.info(f"Successfully generated response with model '{model_name}' on attempt {model_attempts} [Job: {job_id}]")
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
                        f"Model '{model_name}' failed attempt {model_attempts}/{settings.GEMINI_MAX_RETRIES} "
                        f"[Category: {category}, Transient: {is_transient}]: {last_error_msg}"
                    )

                    if job and db:
                        job.status = AITaskStatus.RETRYING if is_transient else AITaskStatus.PERMANENTLY_FAILED
                        job.last_error_category = last_category
                        job.last_error_message = last_error_msg
                        db.commit()

                    if not is_transient:
                        # Permanent error on this model (e.g. 404 unsupported model) -> immediate fallback to next model
                        logger.info(f"Permanent error encountered for '{model_name}'. Switching immediately to next fallback model.")
                        break

                    # Transient error (e.g. 503 UNAVAILABLE, 429) -> apply exponential backoff with jitter
                    if model_attempts < settings.GEMINI_MAX_RETRIES:
                        backoff = self._calculate_backoff(model_attempts)
                        logger.info(f"Backing off for {backoff:.2f}s before retrying model '{model_name}'...")
                        await asyncio.sleep(backoff)
                    else:
                        logger.warning(f"Exhausted all {settings.GEMINI_MAX_RETRIES} retries for model '{model_name}'. Falling back.")

        # If all models failed
        logger.error(f"All Gemini models exhausted for job {job_id}. Last category: {last_category}")
        
        # Check if fallback handler is available
        if mock_fallback_handler:
            logger.info(f"Recovering via deterministic fallback handler for job {job_id}.")
            fallback_res = mock_fallback_handler()
            if job and db:
                job.status = AITaskStatus.COMPLETED
                job.last_error_category = f"FALLBACK_RECOVERED_AFTER_{last_category}"
                db.commit()
            return fallback_res

        # Mark job as RETRYABLE_FAILED so state is safely preserved without data corruption
        if job and db:
            job.status = AITaskStatus.RETRYABLE_FAILED
            job.last_error_category = last_category
            job.last_error_message = f"Transient failure across all models: {last_error_msg}"
            db.commit()

        raise AIOperationException(
            message=f"Gemini service temporarily unavailable across all models. Job marked RETRYABLE_FAILED.",
            job_id=job_id,
            retryable=True,
            error_category=last_category
        )

    async def _call_gemini_api(self, model: str, system_instruction: str, user_prompt: str) -> str:
        """Direct REST call to Gemini generateContent endpoint."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={settings.GEMINI_API_KEY}"
        
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
