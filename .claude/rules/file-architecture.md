---
description: Internal section structure of app.py. Follow this exact ordering when adding new sections. No sub-modules, no separate files.
globs: ["app.py"]
---

# File Architecture — `app.py`

The entire application compiles into a **single `app.py`** file with this exact internal structure:

```
app.py
├── [SECTION 1]  Modal + Anthropic imports and app initialization
├── [SECTION 2]  SCHEMA CONTEXT — hardcoded table metadata (merchants, transactions)
├── [SECTION 3]  SYSTEM PROMPTS — translate_prompt, explain_prompt
├── [SECTION 4]  BACKEND LOGIC — Claude API call functions
├── [SECTION 5]  API ENDPOINTS — Modal @app.function web endpoints
├── [SECTION 6]  HTML_LANDING — landing page as a Python string constant
├── [SECTION 7]  HTML_WORKSPACE — workspace page as a Python string constant
├── [SECTION 8]  ROUTE HANDLERS — serve landing, workspace, and API routes
│
│   ── CDP Module (added after core) ──
├── [SECTION 9]  CDP DATA LAYER — CDP_CRITERIA_FIELDS, CDP_SEGMENTS_LIBRARY, CDP_NL_SYSTEM_PROMPT
├── [SECTION 10] CDP BACKEND LOGIC — build_sql_from_filters, simulate_audience_estimate
├── [SECTION 11] CDP API ENDPOINTS — /api/cdp/segment/estimate, /api/cdp/nl_to_filters, etc.
├── [SECTION 12] HTML_CDP — CDP portal page as a Python string constant
└── [SECTION 13] CDP ROUTE — GET /cdp
```

**Rules:**
- No sub-modules. No separate HTML files. No asset pipeline. Everything self-contained.
- `local_dev.py` mirrors the same routes and serves `.html` files from disk for local development.
- When adding a new page/module, always add a corresponding section in both `app.py` (inline HTML string) and `local_dev.py` (file-read from disk).
