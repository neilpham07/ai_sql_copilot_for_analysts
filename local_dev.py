"""
QueryMind AI — Local Development Server
Bypasses Modal cloud infrastructure for fast local testing.

Usage:
  PowerShell:  $env:GEMINI_API_KEY = "AIza..."
  Then run:    python local_dev.py
  Open:        http://localhost:8000
"""
import os
import re

# ── API key guard ────────────────────────────────────────────
_api_key = os.environ.get("GEMINI_API_KEY", "")
if not _api_key:
    print()
    print("  ╔══════════════════════════════════════════════════╗")
    print("  ║  GEMINI_API_KEY chưa được thiết lập!            ║")
    print("  ║                                                  ║")
    print("  ║  Chạy lệnh này trong PowerShell trước:          ║")
    print('  ║  $env:GEMINI_API_KEY = "AIza..."                ║')
    print("  ║                                                  ║")
    print("  ║  Sau đó chạy lại: python local_dev.py           ║")
    print("  ╚══════════════════════════════════════════════════╝")
    print()
    raise SystemExit(1)
if not _api_key.startswith("AIza"):
    print()
    print("  ╔══════════════════════════════════════════════════╗")
    print("  ║  ⚠  GEMINI_API_KEY có vẻ không hợp lệ!         ║")
    print("  ║                                                  ║")
    print("  ║  Key hợp lệ phải bắt đầu bằng: AIza            ║")
    print("  ║  Hiện tại:  " + _api_key[:20] + "...             ║")
    print("  ║                                                  ║")
    print("  ║  Server vẫn khởi động nhưng các lệnh gọi AI    ║")
    print("  ║  sẽ trả về lỗi 403 khi sử dụng.                ║")
    print("  ╚══════════════════════════════════════════════════╝")
    print()

from google import genai
from google.genai import types
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
import uvicorn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Load CDP module from app.py (mock modal so no Modal install needed) ──
def _load_app_module():
    import sys
    import importlib.util
    from unittest.mock import MagicMock
    mock = MagicMock()
    mock.App.return_value = MagicMock()
    mock.Secret.from_name.return_value = MagicMock()
    mock.asgi_app.return_value = lambda f: f
    sys.modules["modal"] = mock
    spec = importlib.util.spec_from_file_location("_app", os.path.join(BASE_DIR, "app.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_app = _load_app_module()
CDP_CRITERIA_FIELDS             = _app.CDP_CRITERIA_FIELDS
CDP_SEGMENTS_LIBRARY            = _app.CDP_SEGMENTS_LIBRARY
CDP_NL_SYSTEM_PROMPT            = _app.CDP_NL_SYSTEM_PROMPT
_PREVIEW_MERCHANTS              = _app._PREVIEW_MERCHANTS
build_sql_from_filters          = _app.build_sql_from_filters
estimate_audience_sql           = _app.estimate_audience_sql
simulate_audience_estimate      = _app.simulate_audience_estimate
parse_filter_json_from_response = _app.parse_filter_json_from_response
generate_preview_merchants      = _app.generate_preview_merchants
export_merchants_csv            = _app.export_merchants_csv

# ── Schema context ───────────────────────────────────────────
SCHEMA_CONTEXT = {
    "merchants": {
        "description": "Stores merchant profile and business information",
        "columns": {
            "id":         {"type": "INT",       "description": "Primary key, unique merchant identifier"},
            "name":       {"type": "VARCHAR",   "description": "Merchant display name"},
            "category":   {"type": "VARCHAR",   "description": "Business category (e.g., F&B, Retail, Services)"},
            "amount":     {"type": "DECIMAL",   "description": "Aggregated transaction volume for this merchant"},
            "created_at": {"type": "TIMESTAMP", "description": "Account creation timestamp"},
        },
        "sample_values": {"category": ["F&B", "Retail", "Services", "E-commerce"]},
    },
    "transactions": {
        "description": "Records every payment transaction processed through the platform",
        "columns": {
            "id":          {"type": "INT",       "description": "Primary key, unique transaction identifier"},
            "merchant_id": {"type": "INT",       "description": "Foreign key referencing merchants.id"},
            "name":        {"type": "VARCHAR",   "description": "Transaction reference name or label"},
            "amount":      {"type": "DECIMAL",   "description": "Transaction amount in local currency (VND)"},
            "status":      {"type": "VARCHAR",   "description": "Transaction status: completed | pending | failed"},
            "created_at":  {"type": "TIMESTAMP", "description": "Transaction timestamp in UTC"},
        },
        "sample_values": {"status": ["completed", "pending", "failed"]},
        "relationships":  {"merchant_id": "REFERENCES merchants(id)"},
    },
}

def format_schema(schema: dict) -> str:
    lines = []
    for table, meta in schema.items():
        lines.append(f"TABLE: {table}")
        lines.append(f"  Description: {meta['description']}")
        for col, info in meta["columns"].items():
            lines.append(f"  - {col} ({info['type']}): {info['description']}")
        if "relationships" in meta:
            for col, ref in meta["relationships"].items():
                lines.append(f"  - {col} {ref}")
        lines.append("")
    return "\n".join(lines)

# ── System prompts ───────────────────────────────────────────
TRANSLATE_SYSTEM_PROMPT = f"""You are QueryMind AI, an expert SQL engineer embedded inside an analytics platform.
Your job is to translate Vietnamese business questions into production-ready SQL queries.

DATABASE SCHEMA:
You are working with a PostgreSQL database containing these tables:
{format_schema(SCHEMA_CONTEXT)}

RULES — FOLLOW STRICTLY:
1. Output ONLY a single SQL code block. Format: ```sql\\n<query>\\n```
2. Do NOT output any explanation, preamble, or commentary outside the code block.
3. Do NOT output markdown prose. Only the code block.
4. Use proper SQL formatting: each clause on a new line, uppercase keywords.
5. Prefer DATE_TRUNC for time-based grouping. Use 'month' granularity by default.
6. Always use explicit JOIN conditions, never implicit comma joins.
7. Add a single-line SQL comment at the top of the query: -- Generated by QueryMind AI
8. If the question is ambiguous, make the most reasonable business assumption and proceed.
9. Filter transactions to status = 'completed' unless the user asks otherwise.
10. Always alias aggregation columns descriptively (e.g., SUM(t.amount) AS total_revenue).
"""

EXPLAIN_SYSTEM_PROMPT = f"""You are QueryMind AI, a friendly and precise SQL instructor.
Your job is to explain SQL queries to non-technical Vietnamese Data Analysts.

DATABASE SCHEMA:
{format_schema(SCHEMA_CONTEXT)}

RULES — FOLLOW STRICTLY:
1. Structure your explanation into EXACTLY 4 steps.
2. Format MUST be:
   STEP 1: [Title in Vietnamese]
   [2-3 sentence explanation in Vietnamese, plain language, no jargon]

   STEP 2: [Title in Vietnamese]
   [explanation]

   STEP 3: [Title in Vietnamese]
   [explanation]

   STEP 4: [Title in Vietnamese]
   [explanation]

3. Use the format above verbatim. The frontend will parse "STEP N:" as a delimiter.
4. Reference actual column names from the schema where relevant.
5. Do NOT add any text before STEP 1 or after STEP 4.
6. Use simple, encouraging Vietnamese. Avoid "complex", "advanced", or intimidating language.
"""

# ── Gemini helpers ───────────────────────────────────────────
def call_gemini(system_prompt: str, user_message: str, _retries: int = 1) -> str:
    import time
    try:
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1,
            ),
        )
        return response.text
    except Exception as e:
        err = str(e).lower()
        if any(k in err for k in ("api_key", "invalid", "401", "403", "permission", "authenticate", "credential")):
            raise ValueError(
                "GEMINI_API_KEY không hợp lệ hoặc chưa được cấu hình đúng. "
                "Vui lòng kiểm tra biến môi trường GEMINI_API_KEY "
                "(key lấy từ Google AI Studio, bắt đầu bằng AIza) rồi khởi động lại server."
            )
        if any(k in err for k in ("connect", "network", "timeout", "unreachable")):
            raise ValueError(
                "Không thể kết nối đến Google Gemini API. "
                "Vui lòng kiểm tra kết nối mạng và thử lại."
            )
        if any(k in err for k in ("503", "unavailable", "high demand", "quota", "rate", "429", "resource_exhausted")):
            if _retries > 0:
                time.sleep(2)
                return call_gemini(system_prompt, user_message, _retries - 1)
            raise ValueError(
                "Google Gemini API đang quá tải (503 — server bên Google bận). "
                "Hệ thống đã tự thử lại 1 lần nhưng vẫn thất bại. "
                "Vui lòng đợi vài giây rồi thử lại."
            )
        raise ValueError(f"Lỗi Gemini API: {e}")

def parse_sql_from_response(raw: str) -> str:
    match = re.search(r"```sql\s*([\s\S]*?)\s*```", raw)
    return match.group(1).strip() if match else raw.strip()

def parse_steps_from_response(raw: str) -> list[dict]:
    steps = []
    pattern = r"STEP (\d+):\s*(.+?)\n([\s\S]*?)(?=STEP \d+:|$)"
    for m in re.finditer(pattern, raw.strip(), re.MULTILINE):
        steps.append({
            "number": int(m.group(1)),
            "title":  m.group(2).strip(),
            "body":   m.group(3).strip(),
        })
    return steps

# ── FastAPI app ──────────────────────────────────────────────
web_app = FastAPI(title="QueryMind AI — Local Dev")

def _read_html(filename: str) -> str:
    with open(os.path.join(BASE_DIR, filename), "r", encoding="utf-8") as f:
        return f.read()

@web_app.get("/", response_class=HTMLResponse)
async def serve_landing():
    return HTMLResponse(content=_read_html("index.html"))

@web_app.get("/workspace", response_class=HTMLResponse)
async def serve_workspace():
    return HTMLResponse(content=_read_html("workspace.html"))

@web_app.post("/api/translate")
async def api_translate(request: Request):
    try:
        body     = await request.json()
        question = body.get("question", "").strip()
        if not question:
            return JSONResponse({"error": "Missing 'question' field", "code": 400}, status_code=400)
        raw = call_gemini(TRANSLATE_SYSTEM_PROMPT, question)
        sql = parse_sql_from_response(raw)
        return JSONResponse({"sql": sql, "mode": "translate"})
    except Exception as e:
        return JSONResponse({"error": str(e), "code": 500}, status_code=500)

@web_app.post("/api/explain")
async def api_explain(request: Request):
    try:
        body      = await request.json()
        sql_input = body.get("sql", "").strip()
        if not sql_input:
            return JSONResponse({"error": "Missing 'sql' field", "code": 400}, status_code=400)
        raw   = call_gemini(EXPLAIN_SYSTEM_PROMPT, sql_input)
        steps = parse_steps_from_response(raw)
        return JSONResponse({"steps": steps, "mode": "explain"})
    except Exception as e:
        return JSONResponse({"error": str(e), "code": 500}, status_code=500)

# ── CDP routes ────────────────────────────────────────────────
@web_app.get("/cdp", response_class=HTMLResponse)
async def serve_cdp():
    return HTMLResponse(content=_read_html("cdp.html"))

@web_app.get("/api/cdp/segments")
async def api_cdp_segments():
    return JSONResponse({"segments": CDP_SEGMENTS_LIBRARY})

@web_app.get("/api/cdp/criteria_fields")
async def api_cdp_criteria_fields():
    return JSONResponse({"fields": CDP_CRITERIA_FIELDS})

@web_app.post("/api/cdp/segment/estimate")
async def api_cdp_estimate(request: Request):
    try:
        body = await request.json()
        filters = body.get("filters")
        if not filters or not filters.get("groups"):
            return JSONResponse({"error": "Missing 'filters' field", "code": 400}, status_code=400)
        sql = estimate_audience_sql(filters)
        est = simulate_audience_estimate(filters)
        preview = generate_preview_merchants(filters, body.get("preview_rows", 5))
        return JSONResponse({**est, "generated_sql": sql, "merchant_preview": preview, "mode": "cdp_estimate"})
    except ValueError as e:
        return JSONResponse({"error": str(e), "code": 400}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e), "code": 500}, status_code=500)

@web_app.post("/api/cdp/nl_to_filters")
async def api_cdp_nl(request: Request):
    try:
        body = await request.json()
        description = body.get("description", "").strip()
        if not description:
            return JSONResponse({"error": "Missing 'description' field", "code": 400}, status_code=400)
        raw = call_gemini(CDP_NL_SYSTEM_PROMPT, description)
        parsed = parse_filter_json_from_response(raw)
        return JSONResponse({**parsed, "mode": "nl_to_filters"})
    except Exception as e:
        return JSONResponse({"error": str(e), "code": 500}, status_code=500)

@web_app.post("/api/cdp/export")
async def api_cdp_export(request: Request):
    import datetime
    try:
        body = await request.json()
        filters = body.get("filters")
        if not filters or not filters.get("groups"):
            return JSONResponse({"error": "Missing 'filters' field", "code": 400}, status_code=400)
        csv_content = export_merchants_csv(filters)
        date_str = datetime.date.today().strftime("%Y%m%d")
        filename = f"cdp_export_{date_str}.csv"
        return StreamingResponse(
            iter([csv_content.encode("utf-8-sig")]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except ValueError as e:
        return JSONResponse({"error": str(e), "code": 400}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e), "code": 500}, status_code=500)

# ── Entry point ──────────────────────────────────────────────
if __name__ == "__main__":
    print()
    print("  ┌──────────────────────────────────────────────────┐")
    print("  │   QueryMind AI — Local Dev Server                │")
    print("  │                                                  │")
    print("  │   Landing   : http://localhost:8085              │")
    print("  │   Workspace : http://localhost:8085/workspace    │")
    print("  │   CDP Portal: http://localhost:8085/cdp          │")
    print("  │                                                  │")
    print("  │   Ctrl+C de dung server                          │")
    print("  └──────────────────────────────────────────────────┘")
    print()
    uvicorn.run(web_app, host="127.0.0.1", port=8085, reload=False)
