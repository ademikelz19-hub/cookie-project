import re

INJECTION_PATTERNS = [
    r"(?i)ignore\s+(previous|all)\s+instructions",
    r"(?i)system\s+prompt",
    r"(?i)upload\s+your\s+credentials",
    r"(?i)send\s+(secrets|api\s*key|passwords)",
    r"(?i)run\s+this\s+command",
    r"(?i)curl\s+https?://",
    r"(?i)eval\s*\(",
    r"(?i)bash\s+-c",
]

class PromptInjectionDefense:
    """
    Guarantees webpage content is strictly treated as untrusted text.
    Filters out any attempt to hijack LLM system prompts or steal credentials.
    """

    @staticmethod
    def sanitize(text: str) -> str:
        if not text:
            return ""
        clean = text
        for p in INJECTION_PATTERNS:
            clean = re.sub(p, "[REDACTED_SECURITY_ALERT]", clean)
        return clean.strip()

    @staticmethod
    def contains_adversarial_instructions(text: str) -> bool:
        if not text:
            return False
        return any(re.search(p, text) for p in INJECTION_PATTERNS)
