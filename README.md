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
- `uv` package manager

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd multi-text-task-utility
```

2. Install dependencies:

```bash
uv sync
```

3. Create a `.env` file by copying `.env.example` and replacing the placeholder with your OpenAI API key:
```bash
cp .env.example .env
# Then edit .env and replace the placeholder with your actual API key
```

## Usage

Run the application:

```bash
uv run python src/run_query.py
```

The application will start an interactive session where you can:
- Ask questions to get AI-generated responses
- Type `exit` or `quit` to quit the application

## Testing

Run the test suite using pytest:

```bash
uv run pytest tests/
```

To run tests with verbose output:

```bash
uv run pytest tests/ -v
```

## Limitations

### No Chat History

The system does not maintain chat history or pass previous conversations to the LLM. Each query is processed independently without context from prior interactions.

**Rationale**: 
- **Token Usage Reduction**: Avoiding chat history significantly reduces token consumption, lowering API costs

**Trade-offs**:
- Cannot reference or build upon previous interactions
- May result in repetitive responses if users ask follow-up questions
- Lacks contextual understanding of ongoing conversations

### Other Limitations

1. **Response Length**: Limited to 300 tokens maximum, which may truncate longer explanations
2. **Model Constraints**: Uses GPT-4o-mini, which may have limitations in complex reasoning compared to larger models
3. **Temperature Setting**: Fixed at 0.2 for consistency, which may reduce creativity in some edge cases
4. **PII Detection**: Regex-based PII detection may have false positives or miss variations in PII formats
5. **Moderation Categories**: Relies on OpenAI's predefined moderation categories, which may not cover all edge cases
