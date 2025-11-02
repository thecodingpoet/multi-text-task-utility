import json
import time

from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
from openai.types.chat.chat_completion import ChatCompletion
from openai import APIError
from safety import redact_pii, contains_pii, check_moderation

load_dotenv()

MODEL = "gpt-4o-mini"
PROMPT_TOKEN_COST = 0.15
COMPLETION_TOKEN_COST = 0.60
SYSTEM_PROMPT_PATH = Path("prompts/main_prompt.txt")
METRICS_PATH = Path("metrics/metrics.json")
TEMPERATURE = 0.2
MAX_TOKENS = 300


def log_metrics(entry: dict) -> None:
    """Append a single metric entry to the metrics.json file."""
    try:
        with METRICS_PATH.open("r", encoding="utf-8") as f:
            metrics = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        metrics = []

    metrics.append(entry)
    with METRICS_PATH.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)


def calculate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    """Calculate cost of API usage."""
    return (prompt_tokens / 1_000_000) * PROMPT_TOKEN_COST + (
        completion_tokens / 1_000_000
    ) * COMPLETION_TOKEN_COST


def format_response(content: str) -> str:
    """Format JSON response with error handling."""
    try:
        return json.dumps(json.loads(content), indent=4)
    except json.JSONDecodeError:
        return content


def process_query(
    client: OpenAI, messages: list[dict], query: str
) -> ChatCompletion | None:
    """Send query to the model and return the completion response."""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=TEMPERATURE,
            response_format={"type": "json_object"},
            max_tokens=MAX_TOKENS,
        )
        return response
    except APIError as e:
        print(f"❌  API error: {e}")
        return None


def validate_input(client: OpenAI, query: str) -> str | None:
    """Validate and sanitize user input."""
    moderation = check_moderation(client, query)
    if moderation["flagged"]:
        print("⚠️  Your input may violate content guidelines. Please rephrase.")
        return None

    if contains_pii(query):
        query = redact_pii(query)
        print("🔒  Redacted sensitive information.")

    return query


def validate_output(client: OpenAI, content: str) -> bool:
    """Validate API response content."""
    try:
        answer = json.loads(content).get("answer", "")
    except json.JSONDecodeError:
        answer = content

    moderation = check_moderation(client, answer)
    if moderation["flagged"]:
        print("🚫  Response withheld due to policy violation.")
        return False
    return True


def main() -> None:
    """Main function to run the chatbot."""
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")

    client = OpenAI()

    while True:
        query = input("Ask a question: ").strip()

        if not query:
            continue

        if query.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        start_time = time.perf_counter()

        sanitized_query = validate_input(client, query)
        if sanitized_query is None:
            continue

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": sanitized_query},
        ]

        response = process_query(client, messages, sanitized_query)
        if response is None:
            continue

        content = response.choices[0].message.content
        output_blocked = not validate_output(client, content)

        cost = calculate_cost(
            response.usage.prompt_tokens, response.usage.completion_tokens
        )

        latency_ms = (time.perf_counter() - start_time) * 1000

        log_metrics(
            {
                "timestamp": datetime.now().isoformat(),
                "query": sanitized_query,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
                "latency_ms": round(latency_ms, 2),
                "estimated_cost_usd": round(cost, 6),
                "moderation_blocked": output_blocked,
            }
        )

        if not output_blocked:
            print(format_response(content))


if __name__ == "__main__":
    main()
