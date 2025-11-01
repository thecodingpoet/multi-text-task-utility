import re
from openai import OpenAI

PII_PATTERNS = {
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "phone": r"\b(\+?\d{1,3}[\s-]?)?(\(?\d{3}\)?[\s-]?)?\d{3}[\s-]?\d{4}\b",
    "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
}
MODERATION_MODEL = "omni-moderation-latest"


def redact_pii(text: str) -> str:
    """Redact any PII from the text."""
    redacted = text
    for label, pattern in PII_PATTERNS.items():
        redacted = re.sub(pattern, f"[REDACTED-{label.upper()}]", redacted)
    return redacted


def contains_pii(text: str) -> bool:
    """Check if the text contains any PII."""
    return any(re.search(p, text) for p in PII_PATTERNS.values())


def check_moderation(client: OpenAI, text: str) -> dict:
    """Use OpenAI's moderation model to flag unsafe content."""
    response = client.moderations.create(model=MODERATION_MODEL, input=text)
    results = response.results[0]

    categories = results.categories
    flagged = results.flagged

    try:
        categories_dict = categories.model_dump()
    except AttributeError:
        categories_dict = categories.dict()
    flagged_categories = [k for k, v in categories_dict.items() if v]

    return {
        "flagged": flagged,
        "categories": flagged_categories,
    }
