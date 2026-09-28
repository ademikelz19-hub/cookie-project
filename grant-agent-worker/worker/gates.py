import re
from typing import Optional, Tuple
from bs4 import BeautifulSoup
from app.models.enums import InterventionType

class HumanGateDetector:
    """
    Detects when external webpage mandates human intervention.
    Invariants:
    - Never bypass CAPTCHA.
    - Never forge OTP codes.
    - Never auto-sign legal declarations.
    """

    @staticmethod
    def inspect_page(html: str) -> Tuple[bool, InterventionType, Optional[str]]:
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text().lower()

        # 1. CAPTCHA detection
        captcha_selectors = [
            "iframe[src*='recaptcha']",
            "iframe[src*='hcaptcha']",
            "iframe[src*='challenges.cloudflare.com']",
            ".g-recaptcha",
            "#cf-turnstile",
            ".h-captcha"
        ]
        for sel in captcha_selectors:
            if soup.select(sel) or "captcha" in text:
                return True, InterventionType.CAPTCHA, "CAPTCHA verification detected. Human intervention required."

        # 2. OTP / Passkey detection
        otp_patterns = [r"one-time password", r"enter.*6-digit", r"verification code", r"two-factor", r"otp_code"]
        for p in otp_patterns:
            if re.search(p, text) or soup.select("input[name*='otp'], input[id*='otp']"):
                return True, InterventionType.OTP, "Two-factor authentication code or OTP requested by grant portal."

        # 3. Email Verification Link detection
        if "check your email" in text or "we sent a verification link" in text:
            return True, InterventionType.EMAIL_VERIFICATION, "Grant portal requires email confirmation before continuing."

        # 4. Identity / Biometrics
        if "upload your passport" in text or "identity verification" in text or "kyc" in text:
            return True, InterventionType.IDENTITY_VERIFICATION, "Identity / KYC verification requested."

        return False, InterventionType.NONE, None
