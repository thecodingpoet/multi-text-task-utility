from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

import json
import time

load_dotenv()


def log_metrics(query, response, latency_ms, cost):
    """Log metrics to metrics.json"""
    metrics_path = Path("metrics/metrics.json")

    if metrics_path.exists() and metrics_path.stat().st_size > 0:
        with open(metrics_path, "r", encoding="utf-8") as f:
            metrics = json.load(f)
    else:
        metrics = []

    metric_entry = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "latency_ms": round(latency_ms, 2),
        "total_tokens": response.usage.total_tokens,
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "cost": round(cost, 6),
        "model": "gpt-4o-mini",
    }

    metrics.append(metric_entry)
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)


def calculate_cost(prompt_tokens, completion_tokens):
    return (prompt_tokens / 1_000_000) * 0.15 + (completion_tokens / 1_000_000) * 0.60


with open("prompts/main_prompt.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()

messages = [
    {
        "role": "system",
        "content": system_prompt,
    }
]

client = OpenAI()

while True:
    query = input("Enter a query (or 'exit' to quit): ")

    if query == "exit":
        break

    user_prompt = (
        f"User: {query}\n\nReturn only valid JSON in the exact structure shown above."
    )

    messages.append({"role": "user", "content": user_prompt})

    start = time.perf_counter()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
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

    log_metrics(query, response, latency_ms, cost)

    print(json.dumps(json.loads(response.choices[0].message.content), indent=4))
