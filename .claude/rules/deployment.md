---
description: Modal Cloud deployment configuration and local dev server setup. One command to deploy, one command to run locally.
globs: ["app.py", "local_dev.py"]
---

# Deployment

## Modal Cloud (Production)

```python
import modal

app = modal.App("querymind-ai")

@app.function(
    secrets=[modal.Secret.from_name("anthropic-api-key")],
)
@modal.asgi_app()
def fastapi_app():
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse, JSONResponse
    app = FastAPI()
    # ... routes attached here
    return app
```

**Deploy command:**
```bash
modal deploy app.py
```

**Secret setup:** In Modal dashboard, create secret named exactly `"anthropic-api-key"` with key `ANTHROPIC_API_KEY`.

## Local Development

```bash
python local_dev.py
# → http://localhost:8000
```

`local_dev.py` mirrors all routes from `app.py` but serves `.html` files from disk via `_read_html("filename.html")` instead of inline Python string constants. This means local HTML edits are reflected immediately without restarting (except if Python logic changes).

**Windows startup (avoid Unicode encoding errors):**
```powershell
$env:PYTHONIOENCODING = "utf-8"
python local_dev.py
```

## Sync Rule: `app.py` vs `local_dev.py`

When you add a new page or route:
1. Add the inline HTML string constant to `app.py` (e.g., `HTML_CDP = """..."""`)
2. Add the corresponding disk-read route to `local_dev.py` (e.g., `_read_html("cdp.html")`)
3. Both must serve identical content — `cdp.html` is the source of truth; `HTML_CDP` in `app.py` must stay in sync manually.
