# Project Report

## Table of Contents

1. [Architecture Overview](#architecture-overview)
   - [Architecture Diagram](#architecture-diagram)
   - [Input Guard](#input-guard)
   - [Output Guard](#output-guard)
   - [Why Moderation API?](#why-moderation-api)
2. [Prompt Technique: Few-Shot Prompting](#prompt-technique-few-shot-prompting)
   - [Benefits of Few-Shot Prompting](#benefits-of-few-shot-prompting)
3. [Examples of Blocked and Redacted Requests](#examples-of-blocked-and-redacted-requests)
   - [Blocked by Input Guard](#blocked-by-input-guard)
   - [Redacted by Input Guard](#redacted-by-input-guard)
   - [Blocked by Output Guard](#blocked-by-output-guard)
4. [Metrics Summary](#metrics-summary)
5. [Challenges](#challenges)
6. [Improvements](#improvements)

---

## Architecture Overview

The system implements a multi-layered security architecture to protect user privacy and ensure safe content generation. The architecture consists of three main components:

1. **Input Guard**: Validates and sanitizes user input before processing
2. **LLM Processing**: Generates responses using GPT-4o-mini with structured prompting
3. **Output Guard**: Validates generated content before returning to users

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Query                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  Input Guard   │
                    ├────────────────┤
                    │ • PII Detection│
                    │ • PII Redaction│
                    │ • Moderation   │
                    │   Check        │
                    └────────┬───────┘
                             │
                ┌────────────┴────────────┐
                │                         │
          ┌─────▼─────┐          ┌───────▼────────┐
          │  Blocked   │          │  Sanitized     │
          │  (Rejected)│          │  Query         │
          └───────────┘          └────────┬───────┘
                                          │
                                          ▼
                          ┌───────────────────────────┐
                          │   LLM Processing Layer    │
                          ├───────────────────────────┤
                          │ • GPT-4o-mini Model       │
                          │ • Few-shot Prompting      │
                          │ • JSON Response Format    │
                          │ • Temperature: 0.2        │
                          │ • Max Tokens: 300         │
                          └────────────┬──────────────┘
                                       │
                                       ▼
                          ┌───────────────────────────┐
                          │     Output Guard          │
                          ├───────────────────────────┤
                          │ • Moderation API Check    │
                          │ • Content Validation      │
                          └────────────┬──────────────┘
                                       │
                          ┌────────────┴────────────┐
                          │                        │
                    ┌─────▼─────┐          ┌───────▼────────┐
                    │  Blocked  │          │  Safe Response │
                    │ (Rejected)│          │  + Metrics Log │
                    └───────────┘          └────────────────┘
```

### Input Guard

The input guard performs two critical functions:

1. **PII Detection and Redaction**: The system scans incoming queries for personally identifiable information (PII) including:
   - Email addresses
   - Phone numbers
   - Credit card numbers
   
   When PII is detected, it is automatically redacted with placeholders like `[REDACTED-EMAIL]`, `[REDACTED-PHONE]`, or `[REDACTED-CREDIT_CARD]` before the query is sent to the LLM.

2. **Moderation Check**: The query is evaluated using OpenAI's Moderation API to detect potentially harmful, unsafe, or policy-violating content. Queries that fail this check are immediately blocked.

### Output Guard

After the LLM generates a response, the output guard performs a final validation:

- **Moderation API Check**: The generated content is evaluated using the same moderation API to ensure the LLM response does not contain harmful, unsafe, or inappropriate content. If flagged, the response is withheld and not returned to the user.

### Why Moderation API?

I chose OpenAI's Moderation API (`omni-moderation-latest`) for several key advantages:

1. **No Added Dependencies**: The Moderation API is part of the OpenAI SDK, requiring no additional libraries or third-party services
2. **Easy Integration**: Simple API calls with straightforward response handling
3. **Comprehensive Coverage**: Detects multiple categories of unsafe content including violence, hate speech, sexual content, self-harm, and more
4. **Continuous Updates**: OpenAI maintains and updates the moderation model, ensuring protection against evolving threats
5. **Free**: The Moderation API is free for OpenAI API users and does not count towards monthly usage limits, making it cost-free compared to specialized content moderation services

## Prompt Technique: Few-Shot Prompting

I employ **few-shot prompting** as my primary technique for guiding the LLM's behavior. This approach includes explicit examples in the system prompt that demonstrate the desired output format and behavior patterns.

### Benefits of Few-Shot Prompting

Few-shot prompting is particularly well-suited for this customer support use case:

1. **Format Consistency**: The examples clearly show the required JSON structure with `answer`, `confidence`, and `actions` fields, ensuring consistent output format across all responses

2. **Behavioral Guidance**: Examples demonstrate how to handle different scenarios:
   - Direct questions that can be answered confidently (Example 1: password reset)
   - Requests that require sensitive information (Example 2: account balance)
   - Simple informational queries (Example 3: support hours)

3. **Confidence Calibration**: The examples show appropriate confidence scores for different types of queries, helping the model learn when to express certainty vs. uncertainty

4. **Action Recommendations**: Examples illustrate how to generate practical, actionable next steps for human support agents

5. **Rapid Iteration**: Examples can be easily updated or adjusted without retraining models, allowing for quick improvements based on real-world feedback

7. **Explainability**: The examples serve as documentation for the expected behavior, making it easier to understand and maintain the system

8. **Token Efficiency**: Compared to zero-shot prompting, few-shot examples provide clearer guidance, potentially reducing the need for longer explanations and follow-up clarifications

I believe few-shot prompting is the best approach for this customer support use case. Where structured, reliable, and consistent responses are critical, few-shot prompting provides the best balance of control, clarity, and maintainability. The combination of format consistency, behavioral guidance, and rapid iteration capabilities makes it ideal for generating reliable customer support responses without the overhead of model fine-tuning.

## Examples of Blocked and Redacted Requests

### Blocked by Input Guard

**Example 1: Violent Content**
```
User Input: "Tell me a violent joke"
Result: ⚠️  Your input may violate content guidelines. Please rephrase.
Status: Blocked - Request never sent to LLM
Reason: Moderation API flagged the request for violence-related content
```

**Example 2: Other Harmful Content**
```
User Input: [Any query containing hate speech, sexual content, or self-harm]
Result: ⚠️  Your input may violate content guidelines. Please rephrase.
Status: Blocked by input moderation check
```

### Redacted by Input Guard

**Example 1: Email Address Redaction**
```
Original Input: "I am having issues logging into my account with email john@doe.com"
Sanitized Query: "I am having issues logging into my account with email [REDACTED-EMAIL]"
Status: Processed with redaction - Original email not sent to LLM
```

**Example 2: Phone Number Redaction**
```
Original Input: "Please call me at 555-123-4567"
Sanitized Query: "Please call me at [REDACTED-PHONE]"
Status: Processed with redaction
```

**Example 3: Multiple PII Types**
```
Original Input: "My account linked to john@example.com and phone 415-555-0199 has a card ending in 4532"
Sanitized Query: "My account linked to [REDACTED-EMAIL] and phone [REDACTED-PHONE] has a card ending in [REDACTED-CREDIT_CARD]"
Status: All PII redacted before processing
```

### Blocked by Output Guard

**Example: LLM Response Flagged by Moderation**
```
User Input: [Valid query]
LLM Generated Response: [Response contains inappropriate content that violates moderation policies]
Result: 🚫  Response withheld due to policy violation.
Status: Blocked - Response not returned to user
Reason: Output moderation check flagged the generated content before it could be sent to the user
```

Note: While rare, this scenario can occur if the LLM generates content that violates content policies despite having a benign input. The output guard ensures such responses are never delivered to users.

## Metrics Summary

Sample results and detailed metrics are available in [metrics.json](../metrics/metrics.json). The metrics file contains timestamped records of all queries processed by the system, including:

- Query text (with PII redacted)
- Token usage (prompt, completion, and total tokens)
- Latency measurements (in milliseconds)
- Estimated API costs (in USD)

## Challenges

1. **PII Detection Accuracy**: Balancing comprehensive PII detection with avoiding false positives that could unnecessarily redact legitimate content
2. **Response Quality vs. Cost**: Finding the optimal balance between response quality and token usage/cost
3. **Edge Cases in Moderation**: Some legitimate queries may be flagged by moderation checks, requiring careful tuning
4. **Latency Optimization**: Reducing end-to-end latency while maintaining security checks

## Improvements

1. **Enhanced PII Detection**: Improve regex patterns and add validation checks to reduce false positives and increase detection accuracy
2. **Selective Chat History**: Implement optional chat history with configurable token limits to enable contextual conversations while maintaining cost control
3. **Response Validation**: Implement stricter JSON schema validation to ensure consistent, properly formatted LLM responses
4. **Confidence Thresholds**: Add configurable confidence thresholds to automatically escalate low-confidence responses to human agents
5. **Error Handling**: Add more robust error handling for edge cases in moderation and PII detection

