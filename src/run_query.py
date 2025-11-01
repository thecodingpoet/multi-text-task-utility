import json, time

from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from openai.types.chat.chat_completion import ChatCompletion
from safety import redact_pii, contains_pii, check_moderation

load_dotenv()

MODEL = "gpt-4o-mini"
PROMPT_TOKEN_COST = 0.15
COMPLETION_TOKEN_COST = 0.60
SYSTEM_PROMPT_PATH = Path("prompts/main_prompt.txt")


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


def process_query(client: OpenAI, messages: list[dict], query: str) -> ChatCompletion:
    """Process query and return response, and cost."""
    messages.append({"role": "user", "content": query})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.2,
        response_format={"type": "json_object"},
        max_tokens=300,
    )

    return response


def validate_input(client: OpenAI, query: str) -> str | None:
    """Validate and sanitize user input."""
    moderation = check_moderation(client, query)
    if moderation["flagged"]:
        print(
            f"Your input may violate our content guidelines. Flagged categories: {moderation['categories']}"
        )
        return None

    if contains_pii(query):
        query = redact_pii(query)

    return query


def validate_output(client: OpenAI, content: str) -> bool:
    """Validate API response content."""
    moderation = check_moderation(client, content)
    if moderation["flagged"]:
        print(
            "Sorry, I'm unable to share that response as it may contain restricted or unsafe content."
        )
        return False
    return True


def main() -> None:
    """Main function to run the chatbot."""
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    messages = [{"role": "system", "content": system_prompt}]

    client = OpenAI()

    while True:
        query = input("Ask a question or type 'exit' to quit: ")

        start_time = time.perf_counter()

        if query == "exit":
            break

        sanitized_query = validate_input(client, query)
        if sanitized_query is None:
            continue

        response = process_query(client, messages.copy(), sanitized_query)
        if response is None:
            continue

        content = response.choices[0].message.content
        if not validate_output(client, content):
            continue

        cost = calculate_cost(
            response.usage.prompt_tokens, response.usage.completion_tokens
        )

        end_time = time.perf_counter()

        latency_ms = (end_time - start_time) * 1000

        print(f"Latency: {latency_ms:.2f}ms")
        print(f"Cost: ${cost:.6f}")
        print(format_response(content))


if __name__ == "__main__":
    main()
