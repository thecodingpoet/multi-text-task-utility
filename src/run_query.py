import json, time

from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
from safety import redact_pii, contains_pii


load_dotenv()

MODEL = "gpt-4o-mini"
PROMPT_TOKEN_COST = 0.15
COMPLETION_TOKEN_COST = 0.60


def log_metrics(query, response, latency_ms, cost):
    metrics_path = Path("metrics/metrics.json")

    try:
        with metrics_path.open("r", encoding="utf-8") as f:
            metrics = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        metrics = []

    metric_entry = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "latency_ms": round(latency_ms, 2),
        "total_tokens": response.usage.total_tokens,
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "cost": round(cost, 6),
        "model": MODEL,
    }

    metrics.append(metric_entry)
    with metrics_path.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)


def calculate_cost(prompt_tokens, completion_tokens):
    return (prompt_tokens / 1_000_000) * PROMPT_TOKEN_COST + (
        completion_tokens / 1_000_000
    ) * COMPLETION_TOKEN_COST


def format_response(content):
    return json.dumps(json.loads(content), indent=4)


def process_query(client, messages, query):
    messages.append({"role": "user", "content": query})

    start = time.perf_counter()
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.2,
        response_format={"type": "json_object"},
        max_tokens=300,
    )
    end = time.perf_counter()

    latency_ms = (end - start) * 1000
    cost = calculate_cost(
        response.usage.prompt_tokens, response.usage.completion_tokens
    )

    return response, latency_ms, cost


def main():
    system_prompt = Path("prompts/main_prompt.txt").read_text(encoding="utf-8")
    messages = [{"role": "system", "content": system_prompt}]

    client = OpenAI()

    while True:
        query = input("Ask a question or type 'exit' to quit: ")

        if query == "exit":
            break

        moderation = check_moderation(client, query)
        if moderation["flagged"]:
            print(f"⚠️ Your input may violate content guidelines. Please rephrase.")
            continue

        if contains_pii(query):
            query = redact_pii(query)

        response, latency_ms, cost = process_query(client, messages, query)

        log_metrics(query, response, latency_ms, cost)

        print(format_response(response.choices[0].message.content))


if __name__ == "__main__":
    main()
