# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**QueryMind AI** — an AI SQL Copilot for non-technical Vietnamese Data Analysts, extended with a **Finviet CDP Portal** for merchant segmentation. Target: Finviet's 100,000+ retail merchant network.

**Three live pages:**
- `/` — Landing page (`index.html` / `HTML_LANDING`)
- `/workspace` — SQL Copilot (`workspace.html` / `HTML_WORKSPACE`)
- `/cdp` — Finviet CDP Portal (`cdp.html` / `HTML_CDP`)

---

## Development Commands

### Local server (primary workflow)

```powershell
# Windows — must set env var first
$env:PYTHONIOENCODING = "utf-8"
$env:ANTHROPIC_API_KEY = "sk-ant-api03-..."
python local_dev.py
# → http://localhost:8000
```

`local_dev.py` requires: `pip install fastapi uvicorn anthropic`  
`app.py` (Modal deploy) requires: `pip install modal anthropic`

### Modal production deploy

```bash
modal deploy app.py
```

Secret must exist in Modal dashboard: name = `anthropic-api-key`, key = `ANTHROPIC_API_KEY`.

### Smoke-test CDP API

```powershell
# Audience estimate
Invoke-RestMethod -Method POST -Uri http://localhost:8000/api/cdp/segment/estimate `
  -ContentType "application/json" `
  -Body '{"filters":{"operator":"AND","groups":[{"operator":"AND","criteria":[{"field":"gmv_30d","operator":"greater than","value":50000000}]}]}}'

# NLP → filters
Invoke-RestMethod -Method POST -Uri http://localhost:8000/api/cdp/nl_to_filters `
  -ContentType "application/json" `
  -Body '{"description":"Tìm tạp hóa TP HCM có GMV > 50M"}'
```

---

## Architecture

### Two-file duality: `app.py` ↔ `local_dev.py`

`app.py` is the **single deployable artifact** — all Python logic, all HTML pages as inline string constants, no external files. `modal deploy app.py` is the only production deploy command.

`local_dev.py` is the **local dev mirror** — it mocks Modal via `unittest.mock.MagicMock`, then dynamically imports `app.py` via `importlib` to reuse all backend functions (`CDP_CRITERIA_FIELDS`, `build_sql_from_filters`, etc.). It serves HTML from disk (`_read_html("cdp.html")`) instead of inline strings, enabling live HTML edits without restart.

**Sync rule:** Whenever a new page is added to `app.py` as an inline HTML string constant, a matching disk-read route must be added to `local_dev.py`. The `.html` file is the source of truth for local dev; the inline string in `app.py` must stay manually synced.

### `app.py` internal section order

```
[SECTION 1]  Modal + Anthropic imports
[SECTION 2]  SCHEMA_CONTEXT dict (hardcoded, never DB-read)
[SECTION 3]  TRANSLATE_SYSTEM_PROMPT, EXPLAIN_SYSTEM_PROMPT
[SECTION 4]  call_claude(), parse_sql_from_response(), parse_steps_from_response()
[SECTION 5]  @app.function / @modal.asgi_app — fastapi_app()
[SECTION 6]  HTML_LANDING string constant
[SECTION 7]  HTML_WORKSPACE string constant
[SECTION 8]  Route handlers (GET /, /workspace, POST /api/*)
[SECTION 9]  CDP_CRITERIA_FIELDS, CDP_SEGMENTS_LIBRARY, CDP_NL_SYSTEM_PROMPT
[SECTION 10] build_sql_from_filters(), simulate_audience_estimate()
[SECTION 11] CDP API routes (/api/cdp/*)
[SECTION 12] HTML_CDP string constant
[SECTION 13] GET /cdp route
```

### CDP two-tier AI

**Tier 1 (Claude):** `POST /api/cdp/nl_to_filters` — Vietnamese free text → structured filter JSON via `CDP_NL_SYSTEM_PROMPT`. See `.claude/agents/nl_transformer_agent.md` for full field mapping rules.

**Tier 2 (deterministic Python):** `build_sql_from_filters(filters)` → PostgreSQL WHERE clause. No Claude call. This is intentional — deterministic SQL from 200+ field combinations is safer than free-form LLM SQL.

### Client-side auth

All three protected pages (`workspace.html`, `cdp.html`) check `sessionStorage.getItem('qm_auth')` at script load and redirect to `/` if missing. Login modal is on `index.html`. Credentials: `admin@email.com` / `admin123`.

---

## Key Constraints (non-negotiable)

- **Single file deploy:** Everything lives in `app.py`. No sub-modules, no separate HTML files for production.
- **No LangChain / LlamaIndex.** `anthropic` SDK only. Model: `claude-sonnet-4-6`.
- **No Tailwind.** All CSS is inline `<style>` blocks within HTML strings.
- **API key:** Always `os.environ["ANTHROPIC_API_KEY"]`. Never hardcoded.
- **SQL output:** Always strip ` ```sql ` fencing before returning to client.
- **Explain endpoint:** Always returns exactly 4 steps.

---

## `.claude/` Directory Map

```
.claude/
├── CLAUDE.md                        ← this file
├── agents/
│   ├── nl_transformer_agent.md      ← NL→JSON filter mapping rules (Finviet vocabulary, monetary normalization)
│   ├── researcher.md
│   └── reviewer.md
└── rules/                           ← focused rule files (auto-applied by Claude Code)
    ├── technology-constraints.md    ← absolute tech rules + 10 strict code rules
    ├── file-architecture.md         ← app.py section structure
    ├── design-system.md             ← Synthetix Lumina CSS tokens, glassmorphism levels, components
    ├── landing-page.md              ← GET / full spec
    ├── workspace-page.md            ← GET /workspace full spec
    ├── backend-schema-and-prompts.md← SCHEMA_CONTEXT, system prompts, Claude call pattern
    ├── api-endpoints.md             ← all request/response contracts
    ├── frontend-javascript.md       ← auth guard, mode tabs, CDP debounce, toast
    ├── deployment.md                ← Modal config, local dev, app.py ↔ local_dev.py sync rule
    └── cdp-module.md                ← CDP architecture, filter schema, data model, segment library
```

The rules files are the authoritative source for design tokens, API shapes, and field names. When in doubt about a CSS value, an operator name, or a field mapping — read the relevant rule file before writing code.
