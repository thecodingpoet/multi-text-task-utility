import re
from openai import OpenAI

PII_PATTERNS = {
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "phone": r"\b(\+?\d{1,3}[\s-]?)?(\(?\d{3}\)?[\s-]?)?\d{3}[\s-]?\d{4}\b",
    "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
}

def redact_pii(text):
    redacted = text
    for label, pattern in PII_PATTERNS.items():
        redacted = re.sub(pattern, f"[REDACTED-{label.upper()}]", redacted)
    return redacted


def contains_pii(text):
    return any(re.search(p, text) for p in PII_PATTERNS.values())
