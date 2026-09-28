import os
import re
import asyncio
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from playwright.async_api import async_playwright, Page, Browser, TimeoutError as PlaywrightTimeoutError

from worker.injection_guard import PromptInjectionDefense
from worker.gates import HumanGateDetector
from worker.field_mapper import FieldMapper
from app.models.enums import BrowserSessionStatus, InterventionType

class PlaywrightBrowserWorker:
    """
    Isolated Playwright automation worker for navigating official grant portals,
    filling verified applicant data, and uploading approved documents.
    """

    def __init__(self, session_id: str, screenshots_dir: str = "./browser_screenshots"):
        self.session_id = session_id
        self.screenshots_dir = screenshots_dir
        os.makedirs(self.screenshots_dir, exist_ok=True)
        self.page: Optional[Page] = None
        self.browser: Optional[Browser] = None
        self.events: List[Dict[str, Any]] = []

    async def capture_step_screenshot(self, page: Page, step_name: str) -> str:
        filename = f"{self.session_id}_{step_name}.png"
        path = os.path.join(self.screenshots_dir, filename)
        try:
            await page.screenshot(path=path, full_page=False)
        except Exception:
            pass
        return path

    async def execute_application_flow(
        self,
        application_url: str,
        org_data: Dict[str, Any],
        approved_answers: Dict[str, str],
        approved_documents: List[Dict[str, Any]],
        submit_after_approval: bool = False
    ) -> Dict[str, Any]:
        """
        Executes end-to-end browser automation flow safely with human gates.
        """
        parsed_target = urlparse(application_url)
        target_domain = parsed_target.netloc

        async with async_playwright() as p:
            self.browser = await p.chromium.launch(headless=True)
            context = await self.browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            self.page = await context.new_page()

            try:
                # 1. Open official application URL
                self.events.append({"type": "navigating", "url": application_url})
                await self.page.goto(application_url, wait_until="networkidle", timeout=30000)

                # 2. Domain verification
                current_url = self.page.url
                curr_domain = urlparse(current_url).netloc
                if target_domain and curr_domain != target_domain and not curr_domain.endswith(target_domain):
                    self.events.append({
                        "type": "domain_warning",
                        "msg": f"Domain redirected from {target_domain} to {curr_domain}"
                    })

                shot1 = await self.capture_step_screenshot(self.page, "01_page_opened")

                # 3. Check for Prompt Injection in DOM
                content = await self.page.content()
                if PromptInjectionDefense.contains_adversarial_instructions(content):
                    self.events.append({
                        "type": "security_alert",
                        "msg": "Adversarial instructions detected on webpage. Sanitizing untrusted inputs."
                    })
                sanitized_html = PromptInjectionDefense.sanitize(content)

                # 4. Check for Human Intervention Gates (OTP, CAPTCHA, Email verification)
                needs_gate, gate_type, gate_msg = HumanGateDetector.inspect_page(sanitized_html)
                if needs_gate:
                    shot_gate = await self.capture_step_screenshot(self.page, f"gate_{gate_type.value}")
                    await self.browser.close()
                    return {
                        "status": BrowserSessionStatus.WAITING_FOR_USER,
                        "intervention_required": True,
                        "intervention_type": gate_type,
                        "intervention_message": gate_msg,
                        "current_url": current_url,
                        "latest_screenshot_path": shot_gate,
                        "events": self.events,
                        "fields_completed": 0
                    }

                # 5. Field Identification and Filling
                fields_completed = 0
                inputs = await self.page.query_selector_all("input, textarea, select")

                for inp in inputs:
                    tag_name = await (await inp.get_property("tagName")).json_value()
                    tag_lower = tag_name.lower()
                    inp_type = (await inp.get_attribute("type") or "text").lower()
                    inp_id = await inp.get_attribute("id") or ""
                    inp_name = await inp.get_attribute("name") or ""

                    # Find label
                    label_text = ""
                    if inp_id:
                        lbl = await self.page.query_selector(f"label[for='{inp_id}']")
                        if lbl:
                            label_text = await lbl.inner_text()
                    if not label_text:
                        aria = await inp.get_attribute("aria-label")
                        if aria:
                            label_text = aria
                        else:
                            try:
                                parent_text = await inp.evaluate("el => el.closest('label') ? el.closest('label').innerText : ''")
                                if parent_text:
                                    label_text = parent_text
                            except Exception:
                                pass

                    # Determine value
                    val = FieldMapper.map_field_to_value(
                        field_id=inp_id,
                        field_name=inp_name,
                        label_text=label_text,
                        field_type=inp_type,
                        org_data=org_data,
                        approved_answers=approved_answers
                    )

                    if val is not None:
                        try:
                            if tag_lower == "select":
                                await inp.select_option(value=str(val))
                                fields_completed += 1
                            elif inp_type == "checkbox":
                                if val is True:
                                    await inp.check()
                                    fields_completed += 1
                            elif inp_type == "file":
                                # Document upload: strictly only approved documents
                                if approved_documents:
                                    doc_to_upload = approved_documents[0]
                                    doc_path = doc_to_upload.get("storage_path")
                                    if doc_path and os.path.exists(doc_path):
                                        await inp.set_input_files(doc_path)
                                        fields_completed += 1
                                        self.events.append({
                                            "type": "file_uploaded",
                                            "filename": doc_to_upload.get("filename")
                                        })
                            else:
                                await inp.fill(str(val))
                                fields_completed += 1
                        except Exception as e:
                            self.events.append({"type": "field_fill_error", "field": inp_name, "error": str(e)})

                shot_filled = await self.capture_step_screenshot(self.page, "02_fields_completed")

                # 6. Save or Submit Gate
                confirmation_ref = None
                if submit_after_approval:
                    # Submit application
                    submit_btn = await self.page.query_selector("button[type='submit'], input[type='submit'], #submit-application-btn")
                    if submit_btn:
                        try:
                            async with self.page.expect_navigation(timeout=10000):
                                await submit_btn.click()
                        except Exception:
                            await self.page.wait_for_timeout(2000)

                        shot_submitted = await self.capture_step_screenshot(self.page, "03_submitted")
                        final_text = await self.page.inner_text("body")
                        ref_match = re.search(r"(?:Reference|Confirmation):\s*([A-Za-z0-9\-]+)", final_text, re.IGNORECASE)
                        if ref_match:
                            confirmation_ref = ref_match.group(1).strip()
                        elif "OFFICIAL-ADIF-" in final_text:
                            confirmation_ref = re.search(r"(OFFICIAL-ADIF-[A-Za-z0-9]+)", final_text).group(1)

                await self.browser.close()

                return {
                    "status": BrowserSessionStatus.COMPLETED if submit_after_approval else BrowserSessionStatus.WAITING_FOR_USER,
                    "intervention_required": False,
                    "intervention_type": InterventionType.NONE,
                    "current_url": self.page.url,
                    "latest_screenshot_path": shot_filled,
                    "fields_completed": fields_completed,
                    "confirmation_reference": confirmation_ref,
                    "events": self.events
                }

            except Exception as e:
                err_shot = None
                if self.page:
                    err_shot = await self.capture_step_screenshot(self.page, "error")
                if self.browser:
                    await self.browser.close()
                return {
                    "status": BrowserSessionStatus.FAILED,
                    "error_message": str(e),
                    "current_url": self.page.url if self.page else application_url,
                    "latest_screenshot_path": err_shot,
                    "fields_completed": 0,
                    "events": self.events
                }
