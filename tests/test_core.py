"""Unit tests for the multi-text-task-utility."""

import json
from pathlib import Path

import pytest

# Add src to path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from run_query import calculate_cost, format_response
from safety import redact_pii, contains_pii


def test_cost_calculation_basic():
    """Test basic cost calculation."""
    result = calculate_cost(1000000, 500000)  # 1M prompt, 500K completion
    expected = (1 * 0.15) + (0.5 * 0.60)  # $0.15 + $0.30 = $0.45
    assert result == pytest.approx(expected, abs=1e-6)


def test_cost_calculation_zero_tokens():
    """Test cost calculation with zero tokens."""
    result = calculate_cost(0, 0)
    assert result == 0.0


def test_cost_calculation_small_amounts():
    """Test cost calculation with small token counts."""
    result = calculate_cost(1000, 500)
    expected = (1000 / 1_000_000) * 0.15 + (500 / 1_000_000) * 0.60
    assert result == pytest.approx(expected, abs=1e-8)


def test_format_valid_json():
    """Test formatting valid JSON string."""
    json_str = '{"answer": "test", "confidence": 0.9, "actions": ["action1"]}'
    result = format_response(json_str)
    # Should return formatted JSON
    parsed = json.loads(result)
    assert parsed["answer"] == "test"
    assert parsed["confidence"] == 0.9


def test_format_invalid_json():
    """Test formatting invalid JSON returns original string."""
    invalid_json = "not valid json {"
    result = format_response(invalid_json)
    assert result == invalid_json


def test_format_empty_string():
    """Test formatting empty string."""
    result = format_response("")
    assert result == ""


def test_contains_pii_email():
    """Test PII detection with email."""
    text = "Contact me at user@example.com"
    assert contains_pii(text) is True


def test_contains_pii_phone():
    """Test PII detection with phone number."""
    text = "Call me at 555-123-4567"
    assert contains_pii(text) is True


def test_contains_pii_credit_card():
    """Test PII detection with credit card."""
    text = "Card number: 4532-1234-5678-9010"
    assert contains_pii(text) is True


def test_contains_pii_no_pii():
    """Test PII detection with no PII."""
    text = "This is a normal message without any sensitive information."
    assert contains_pii(text) is False


def test_redact_pii_email():
    """Test PII redaction with email."""
    text = "Contact me at user@example.com"
    result = redact_pii(text)
    assert "[REDACTED-EMAIL]" in result
    assert "user@example.com" not in result


def test_redact_pii_phone():
    """Test PII redaction with phone number."""
    text = "Call me at 555-123-4567"
    result = redact_pii(text)
    assert "[REDACTED-PHONE]" in result
    assert "555-123-4567" not in result


def test_redact_pii_multiple():
    """Test PII redaction with multiple types."""
    text = "Email: user@example.com, Phone: 555-123-4567"
    result = redact_pii(text)
    assert "[REDACTED-EMAIL]" in result
    assert "[REDACTED-PHONE]" in result
    assert "user@example.com" not in result
    assert "555-123-4567" not in result


def test_redact_pii_no_pii():
    """Test PII redaction with no PII returns original."""
    text = "This is a normal message."
    result = redact_pii(text)
    assert result == text


def test_format_json_with_nested_structure():
    """Test formatting JSON with nested structure."""
    json_str = '{"answer": "test", "metadata": {"key": "value"}}'
    result = format_response(json_str)
    parsed = json.loads(result)
    assert parsed["metadata"]["key"] == "value"


def test_format_json_with_array():
    """Test formatting JSON with array."""
    json_str = '{"actions": ["action1", "action2", "action3"]}'
    result = format_response(json_str)
    parsed = json.loads(result)
    assert len(parsed["actions"]) == 3
