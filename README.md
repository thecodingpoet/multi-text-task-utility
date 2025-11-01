# Multi-Text Task Utility

A Python application that helps customer support agents by generating concise, factual responses to customer questions. 

## Features

- 🤖 **AI-Powered Responses**: Uses GPT-4o-mini to generate helpful, factual responses to customer queries
- 🔒 **PII Protection**: Automatically detects and redacts sensitive information (emails, phone numbers, credit cards) before sending to the API
- 📊 **Metrics Tracking**: Logs query metrics including latency, token usage, and cost to `metrics/metrics.json`
- 📝 **Structured Output**: Returns responses in JSON format with answer, confidence score, and recommended actions
- 💰 **Cost Monitoring**: Calculates and tracks API costs based on token usage

## Requirements

- Python >= 3.14
- OpenAI API key
- `uv` package manager (recommended) or `pip`

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd multi-text-task-utility
```

2. Install dependencies:

Using `uv` (recommended):
```bash
uv sync
```

Or using `pip`:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory and add your OpenAI API key:
```bash
OPENAI_API_KEY=your_api_key_here
```

## Usage

Run the application:

Using `uv`:
```bash
uv run python src/run_query.py
```

Or using `pip`:
```bash
python src/run_query.py
```

The application will start an interactive session where you can:
- Ask questions to get AI-generated responses
- Type `exit` to quit the application
