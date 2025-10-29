from openai import OpenAI
from dotenv import load_dotenv
import json
import time

load_dotenv()

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

    print(f"Time taken: {latency_ms} milliseconds")

    print("--------------------------------")

    print(f"Total tokens: {response.usage.total_tokens:,}")
    print(f"Prompt tokens: {response.usage.prompt_tokens:,}")
    print(f"Completion tokens: {response.usage.completion_tokens:,}")

    print("--------------------------------")

    cost = (response.usage.prompt_tokens / 1_000_000) * 0.15 + (
        response.usage.completion_tokens / 1_000_000
    ) * 0.60
    print(f"Cost: ${cost:.6f}")

    print("--------------------------------")

    print(json.dumps(json.loads(response.choices[0].message.content), indent=4))
