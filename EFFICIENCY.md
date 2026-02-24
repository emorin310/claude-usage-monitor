# OpenClaw Efficiency Protocol (Feb 2026)

## 1. Model Tiering
- **Research/Fetch:** Use Gemini 1.5 Flash exclusively.
- **Drafting/Boilerplate:** Use DeepSeek V3.
- **Critical Logic/Refactoring:** Escalate to Claude 3.5 Sonnet ONLY after a plan is approved.

## 2. Token Reducers
- Use `fetch` for all web content. Do not let the LLM use its internal "knowledge" for facts.
- Always use the `sequential_thinking` tool before multi-step business or IT tasks.
- If a response is longer than 500 words, pause and ask for permission to continue.

## 3. Homelab Context
- Direct access to HPE servers is via the `terminal` tool.
- Pull server logs into a `.txt` file first; do not read the live output stream (too many tokens).
