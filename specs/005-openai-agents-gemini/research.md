# Research: OpenAI Agents SDK with Gemini Models

**Feature**: 005-openai-agents-gemini  
**Date**: 2026-03-06  
**Status**: Complete

## Research Questions & Findings

### RQ-1: How to configure OpenAI Agents SDK for non-OpenAI providers?

**Decision**: Use `OpenAIChatCompletionsModel` with a custom `AsyncOpenAI` client pointing at Gemini's endpoint.

**Rationale**: The SDK's default `OpenAIResponsesModel` uses the Responses API which Gemini doesn't support. The `OpenAIChatCompletionsModel` uses the standard `chat.completions` API which Gemini fully supports. Three configuration approaches exist:

1. `set_default_openai_client()` — global client replacement
2. `ModelProvider` at `Runner.run()` level
3. `Agent.model` — per-agent model instance

We use approach 3 (per-agent `OpenAIChatCompletionsModel`) for explicit clarity, combined with approach 1 for the shared client.

**Alternatives considered**:
- LiteLLM integration (`openai-agents[litellm]`): Adds unnecessary dependency; Gemini already has native OpenAI compat
- `set_default_openai_api("chat_completions")` global: Works but less explicit; we prefer per-agent model for testability

### RQ-2: Does Gemini's OpenAI-compatible endpoint support embeddings?

**Decision**: YES — Gemini supports `client.embeddings.create(input=..., model="gemini-embedding-001")` via the OpenAI compat layer.

**Rationale**: Google's documentation explicitly shows embeddings working through the OpenAI SDK. This means we can use the same `AsyncOpenAI` client for both generation AND embeddings, removing the `google-genai` SDK entirely.

**Alternatives considered**:
- Keep `google-genai` only for embeddings: Unnecessary since compat layer supports it
- Use a separate `AsyncOpenAI` client for embeddings: Adds complexity; same client works

**Impact**: FR-005 in spec said "keep `google-genai` only for embeddings." Since Gemini's OpenAI compat supports embeddings, we can remove `google-genai` entirely → cleaner dependency tree.

### RQ-3: What model names to use with Gemini's OpenAI-compatible endpoint?

**Decision**: Use `gemini-2.5-flash` for generation and `gemini-embedding-001` for embeddings.

**Rationale**: The current codebase already uses `gemini-2.5-flash` for generation and `gemini-embedding-001` for embeddings. Google's docs show these model names work through the OpenAI compat layer. Newer models like `gemini-3-flash-preview` are available but `gemini-2.5-flash` is stable and proven.

**Alternatives considered**:
- `gemini-3-flash-preview`: Newer but "preview" indicates potential instability
- `gemini-2.5-pro`: Higher quality but slower and more expensive

### RQ-4: How to handle tracing without an OpenAI API key?

**Decision**: Disable tracing with `set_tracing_disabled(True)` at startup.

**Rationale**: The Agents SDK sends traces to OpenAI servers by default, which requires a platform.openai.com API key. Since we're using Gemini exclusively, we have no OpenAI key. Without disabling, we'd get 401 errors on every trace upload.

**Alternatives considered**:
- Set a separate OpenAI key for tracing only: Unnecessary cost/complexity
- Custom trace processor: Over-engineering for our use case

### RQ-5: How does `Runner.run()` return results?

**Decision**: `Runner.run()` returns a `RunResult` object with `final_output` (string), `new_items`, and metadata.

**Rationale**: For our use case (single-agent, text-in/text-out), `result.final_output` gives us the generated text directly. No structured output or tool calls needed for our three agents.

**Code pattern**:
```python
from agents import Agent, Runner, OpenAIChatCompletionsModel, ModelSettings
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

agent = Agent(
    name="tutor",
    instructions="You are a helpful tutor...",
    model=OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=client),
    model_settings=ModelSettings(temperature=0.3, max_tokens=1024),
)

result = await Runner.run(agent, input="What is ROS 2?")
answer = result.final_output  # string
```

### RQ-6: What happens when Gemini returns errors through the OpenAI compat layer?

**Decision**: Errors surface as standard `openai` SDK exceptions (`APIError`, `RateLimitError`, `APITimeoutError`). The Agents SDK wraps these during `Runner.run()`.

**Rationale**: Since we're using the OpenAI SDK client against Gemini's endpoint, error handling follows OpenAI's exception hierarchy. Rate limits (429) come as `RateLimitError`, server errors (500/503) as `APIError`.

**Error handling pattern**: Wrap `Runner.run()` in try/except and map exceptions to HTTP status codes (429→429, 500/503→503).

### RQ-7: Can we remove `groq` and `google-genai` dependencies?

**Decision**: 
- Remove `groq` — no longer used (failover chain replaced by single Gemini agent)
- Remove `google-genai` — embeddings now use OpenAI compat layer
- Keep `openai` — required by `openai-agents`
- Add `openai-agents` — the core new dependency

**Rationale**: Clean dependency tree. The `openai-agents` package depends on `openai` internally. Gemini's OpenAI compat layer handles both generation and embeddings.

**New `requirements.txt`**:
```
fastapi>=0.115.0
uvicorn[standard]>=0.34.0
openai-agents>=0.0.15
qdrant-client>=1.13.0
python-dotenv>=1.0.0
pytest>=8.0.0
httpx>=0.28.0
```

### RQ-8: What is the `openai-agents` package version and stability?

**Decision**: Pin `openai-agents>=0.0.15` (latest stable as of research date; SDK is at v0.10.5).

**Rationale**: The SDK is actively maintained by OpenAI. The `openai-agents` package on PyPI maps to the `openai-agents-python` repository. Version pinning ensures reproducible builds.

**Note**: The `openai-agents` package installs `openai` as a transitive dependency, so we don't need to list `openai` separately in requirements.txt.
