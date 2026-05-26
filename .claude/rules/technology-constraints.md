---
description: Absolute technology constraints for QueryMind AI. Apply to every code change — forbidden frameworks, SDK rules, model selection, and single-file deployment.
globs: ["**/*.py", "**/*.html"]
---

# Technology Constraints — NON-NEGOTIABLE

These rules are absolute. Do NOT deviate.

| Constraint | Rule |
|---|---|
| **Framework** | Modal Cloud Web Endpoint (ASGI/FastAPI built-in). Zero external web frameworks. |
| **AI SDK** | Official `anthropic` Python SDK ONLY. |
| **AI Model** | `claude-sonnet-4-6` (current). Default to latest Sonnet unless instructed otherwise. |
| **LangChain** | FORBIDDEN. Do not import or suggest it. |
| **Heavy frameworks** | FORBIDDEN. No LlamaIndex, Haystack, or similar orchestration layers. |
| **Deployment** | Single file: `app.py`. Deploy with `modal deploy app.py`. Nothing else. |
| **Language** | Python backend. All HTML/CSS/JS is rendered as inline strings within `app.py`. |
| **Dependencies** | `modal`, `anthropic`. No other pip packages. |

## Strict Code Rules

1. **Never invent colors.** Always use exact hex/rgba values from the design system.
2. **Never use Tailwind utility classes.** Write all CSS as inline styles or `<style>` blocks within HTML strings.
3. **Never break the single-file constraint.** All HTML, CSS, JS, and Python live in `app.py`.
4. **Never use LangChain, LlamaIndex, or any orchestration framework.**
5. **Never use `requests` or `httpx` to call Claude.** Use the `anthropic` SDK exclusively.
6. **Never hardcode the Anthropic API key.** Always use `os.environ["ANTHROPIC_API_KEY"]`.
7. **Never remove the schema context** from system prompts. Every Claude call must be schema-aware.
8. **Never output SQL without stripping fencing.** The API must return raw SQL strings.
9. **Always return exactly 4 steps** from the explain endpoint.
10. **Match the mockup images** in `./web_pic/` as the final visual reference. When in doubt, look at the image.

## Modal Secret Configuration

```python
@app.function(
    secrets=[modal.Secret.from_name("anthropic-api-key")],
)
```

The secret **must** be named `"anthropic-api-key"` in the Modal dashboard. Access via `os.environ["ANTHROPIC_API_KEY"]`.
