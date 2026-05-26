---
description: API endpoint contracts for all routes — request/response shapes, error format, and CDP endpoints. Reference when adding or modifying endpoints.
globs: ["app.py", "local_dev.py"]
---

# API Endpoints

## Core Routes

| Method | Path | Handler | Description |
|---|---|---|---|
| `GET` | `/` | `serve_landing` | Landing page |
| `GET` | `/workspace` | `serve_workspace` | Workspace page |
| `GET` | `/cdp` | `serve_cdp` | CDP portal page |
| `POST` | `/api/translate` | `api_translate` | Vietnamese → SQL |
| `POST` | `/api/explain` | `api_explain` | SQL → Step explanation |

## POST `/api/translate`

```python
# Request
{"question": "string"}  # Vietnamese question

# Success response
{"sql": "SELECT ...", "mode": "translate"}  # raw SQL, no markdown fencing

# Error
{"error": "string", "code": 400}
```

## POST `/api/explain`

```python
# Request
{"sql": "string"}  # raw SQL to explain

# Success response
{
  "steps": [
    {"number": 1, "title": "...", "body": "..."},
    {"number": 2, "title": "...", "body": "..."},
    {"number": 3, "title": "...", "body": "..."},
    {"number": 4, "title": "...", "body": "..."}
  ],
  "mode": "explain"
}
```

Always exactly 4 steps.

## CDP Routes

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/cdp/segment/estimate` | Estimate audience size from filter JSON |
| `POST` | `/api/cdp/nl_to_filters` | NLP description → structured filter JSON |
| `GET` | `/api/cdp/segments` | Full segment library for sidebar |
| `GET` | `/api/cdp/criteria_fields` | All filter fields for rule builder dropdowns |

## POST `/api/cdp/segment/estimate`

```json
// Request
{
  "filters": {
    "operator": "AND",
    "groups": [
      {
        "operator": "AND",
        "criteria": [
          {"field": "app_installed_state", "operator": "is exactly", "value": "Installed"},
          {"field": "average_order_value", "operator": "greater than", "value": 1250000}
        ]
      }
    ]
  },
  "segment_name": "High-Value App Users",
  "preview_rows": 5
}

// Success response
{
  "audience_size": 24150,
  "total_merchants": 100000,
  "coverage_pct": 24.15,
  "reach_reliability": 98.5,
  "forecasted_conversion": 19.8,
  "delta_pct": 16.2,
  "generated_sql": "SELECT COUNT(DISTINCT m.id) ...",
  "merchant_preview": [
    {
      "merchant_store": "Tạp Hóa Cô Mai",
      "region": "TP. HCM",
      "segment_tag": "Active Champion",
      "gmv_30d": 4210000,
      "cdp_status": "Excellent"
    }
  ],
  "mode": "cdp_estimate"
}

// Error
{"error": "Unknown field: xyz", "code": 400}
```

## POST `/api/cdp/nl_to_filters`

```json
// Request
{"description": "Merchant TP HCM có GMV > 50M, đã cài app, hoạt động liên tục 3 tháng"}

// Response
{"filters": {...}, "confidence": 0.92, "mode": "nl_to_filters"}
```
