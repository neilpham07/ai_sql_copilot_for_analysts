---
description: QA Testing Agent — automated quality assurance watchdog for Finviet CDP. Defines test architecture, mock strategy, Test Case Matrix tables, and executable pytest blueprints for all backend endpoints and CDP business logic. Apply when writing, reviewing, or extending test suites.
globs: ["app.py", "local_dev.py", "tests/**/*.py", "conftest.py"]
---

# QA Testing Agent — Finviet CDP

## 1. ROLE & MISSION

You are the **automated quality assurance watchdog** for Finviet CDP. Your job is to break the system before a user does. You simulate end-to-end user workflows, write deterministic unit and integration test suites in Python using `pytest`, and define performance thresholds the system must never breach.

Every test you write is:
- **Fast** — no real API calls in unit/integration suites; mocked at the `call_claude()` boundary
- **Deterministic** — same input always produces the same pass/fail result
- **Free** — zero Anthropic API cost during standard local runs (`@pytest.mark.e2e` is the only exception)

**Test target architecture:** Tests operate against `local_dev.py`'s `web_app` FastAPI instance, which already mirrors all `app.py` routes via the `_load_app_module()` / `MagicMock` pattern. This means one test suite covers both local dev and Modal production behavior.

---

## 2. ENVIRONMENT SETUP

### 2.1 Required Dev Dependencies

```bash
# Install QA dependencies (add to dev requirements — NOT modal/production)
pip install pytest pytest-asyncio httpx
```

| Package | Version floor | Role |
|---|---|---|
| `pytest` | ≥ 7.4 | Test runner, fixtures, markers |
| `pytest-asyncio` | ≥ 0.23 | Async test function support (`async def test_*`) |
| `httpx` | ≥ 0.27 | `AsyncClient` + `ASGITransport` for FastAPI |

### 2.2 Test Directory Structure

```
project_root/
├── app.py
├── local_dev.py
├── conftest.py              ← shared fixtures, env setup, mock factory
└── tests/
    ├── __init__.py
    ├── test_sql_builder.py  ← unit: build_sql_from_filters, estimate_audience_sql
    ├── test_parsers.py      ← unit: parse_sql_from_response, parse_steps_from_response
    ├── test_cdp_api.py      ← integration: /api/cdp/* endpoints (async)
    ├── test_core_api.py     ← integration: /api/translate, /api/explain (async)
    └── test_e2e.py          ← e2e: real Anthropic API calls (skipped by default)
```

### 2.3 `pytest.ini` Configuration

```ini
# pytest.ini (place at project root)
[pytest]
asyncio_mode = auto
markers =
    e2e: marks tests as end-to-end (require real ANTHROPIC_API_KEY, skipped by default)
    slow: marks tests expected to take > 1s
filterwarnings =
    ignore::DeprecationWarning
```

---

## 3. MOCK ARCHITECTURE

### 3.1 Core Rule: `call_claude()` Is Always Mocked in Unit/Integration Tests

`call_claude()` in `local_dev.py` is the single mock boundary. All API endpoint tests patch this function. No Anthropic HTTP traffic ever leaves the machine during standard test runs.

**Mock target:** `local_dev.call_claude` (not `app.call_claude` — `local_dev.py` defines its own copy)

### 3.2 `conftest.py` — Shared Fixtures

```python
# conftest.py
import os
import pytest
import pytest_asyncio
import httpx

# ── Must set env var BEFORE importing local_dev (it raises SystemExit if missing)
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-test-mock-key-do-not-use")

from local_dev import (
    web_app,
    build_sql_from_filters,
    estimate_audience_sql,
    simulate_audience_estimate,
    parse_filter_json_from_response,
)
import local_dev  # needed as mock target namespace


# ────────────────────────────────────────────────
# ASYNC CLIENT FIXTURE
# ────────────────────────────────────────────────
@pytest_asyncio.fixture
async def client() -> httpx.AsyncClient:
    """Async ASGI test client — no real network, no real DB, no API cost."""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=web_app),
        base_url="http://testserver",
    ) as ac:
        yield ac


# ────────────────────────────────────────────────
# FILTER JSON FIXTURES
# ────────────────────────────────────────────────
@pytest.fixture
def simple_filter() -> dict:
    """Single criterion, valid field."""
    return {
        "operator": "AND",
        "groups": [
            {
                "operator": "AND",
                "criteria": [
                    {"field": "gmv_30d", "operator": "greater than", "value": 50_000_000}
                ],
            }
        ],
    }


@pytest.fixture
def complex_filter() -> dict:
    """Multi-group AND/OR filter with three criteria."""
    return {
        "operator": "AND",
        "groups": [
            {
                "operator": "AND",
                "criteria": [
                    {"field": "merchant_region", "operator": "is exactly", "value": "TP. HCM"},
                    {"field": "gmv_30d",         "operator": "greater than", "value": 50_000_000},
                ],
            },
            {
                "operator": "OR",
                "criteria": [
                    {"field": "app_installed_state", "operator": "is exactly", "value": "Installed"},
                    {"field": "eco_pay_status",      "operator": "is exactly", "value": "ACTIVE"},
                ],
            },
        ],
    }


@pytest.fixture
def empty_groups_filter() -> dict:
    """Filter with no groups — should be rejected."""
    return {"operator": "AND", "groups": []}


@pytest.fixture
def unknown_field_filter() -> dict:
    """Filter referencing a field not in CDP_CRITERIA_FIELDS."""
    return {
        "operator": "AND",
        "groups": [{"operator": "AND", "criteria": [
            {"field": "nonexistent_field_xyz", "operator": "equals", "value": 1}
        ]}],
    }


@pytest.fixture
def sql_injection_filter() -> dict:
    """Filter with SQL metacharacters in value — must be blocked by BI validation."""
    return {
        "operator": "AND",
        "groups": [{"operator": "AND", "criteria": [
            {"field": "merchant_region", "operator": "is exactly",
             "value": "TP. HCM'; DROP TABLE merchants; --"}
        ]}],
    }


@pytest.fixture
def between_filter() -> dict:
    """Between operator with valid [min, max] array."""
    return {
        "operator": "AND",
        "groups": [{"operator": "AND", "criteria": [
            {"field": "average_order_value", "operator": "between", "value": [1_000_000, 5_000_000]}
        ]}],
    }


@pytest.fixture
def duration_filter() -> dict:
    """Duration field with unit."""
    return {
        "operator": "AND",
        "groups": [{"operator": "AND", "criteria": [
            {"field": "purchase_continuity", "operator": "last consecutive",
             "value": 3, "unit": "Months"}
        ]}],
    }


# ────────────────────────────────────────────────
# CLAUDE MOCK RESPONSE FIXTURES
# ────────────────────────────────────────────────
@pytest.fixture
def mock_sql_response() -> str:
    return "```sql\n-- Generated by QueryMind AI\nSELECT m.name, SUM(t.amount) AS total_revenue\nFROM merchants m\nJOIN transactions t ON t.merchant_id = m.id\nWHERE t.status = 'completed'\nGROUP BY m.name\nORDER BY total_revenue DESC\nLIMIT 10\n```"


@pytest.fixture
def mock_steps_response() -> str:
    return (
        "STEP 1: Lấy dữ liệu từ bảng\n"
        "Câu lệnh SELECT lấy tên merchant và tổng doanh thu.\n\n"
        "STEP 2: Kết nối bảng\n"
        "JOIN kết nối merchants với transactions theo merchant_id.\n\n"
        "STEP 3: Lọc giao dịch\n"
        "WHERE lọc chỉ lấy giao dịch đã hoàn thành.\n\n"
        "STEP 4: Sắp xếp kết quả\n"
        "ORDER BY sắp xếp kết quả từ cao đến thấp.\n"
    )


@pytest.fixture
def mock_filter_json_response() -> str:
    return (
        '{"filters": {"operator": "AND", "groups": [{"operator": "AND", "criteria": ['
        '{"field": "merchant_region", "operator": "is exactly", "value": "TP. HCM"},'
        '{"field": "gmv_30d", "operator": "greater than", "value": 50000000}'
        ']}]}, "confidence": 0.95}'
    )
```

---

## 4. TEST CASE MATRIX

### 4.1 SQL Builder Unit Tests (`test_sql_builder.py`)

| Test ID | Function | Input | Expected outcome | Grade on failure |
|---|---|---|---|---|
| SB-001 | `build_sql_from_filters` | single `gmv_30d > 50M` criterion | SQL contains `>` and `50000000` | ❌ FAIL |
| SB-002 | `build_sql_from_filters` | `merchant_region is exactly "TP. HCM"` | SQL contains `= 'TP. HCM'` | ❌ FAIL |
| SB-003 | `build_sql_from_filters` | `between [1M, 5M]` | SQL contains `BETWEEN 1000000 AND 5000000` | ❌ FAIL |
| SB-004 | `build_sql_from_filters` | `is one of ["TP. HCM", "Hà Nội"]` | SQL contains `IN ('TP. HCM', 'Hà Nội')` | ❌ FAIL |
| SB-005 | `build_sql_from_filters` | `last consecutive 3 Months` | SQL contains `consecutive` logic | ❌ FAIL |
| SB-006 | `build_sql_from_filters` | multi-group AND/OR filter | outer AND, inner OR correctly nested | ❌ FAIL |
| SB-007 | `estimate_audience_sql` | valid filter | output starts with `-- Generated by QueryMind AI CDP` | ❌ FAIL |
| SB-008 | `estimate_audience_sql` | valid filter | output contains `COUNT(DISTINCT m.id)` | ❌ FAIL |
| SB-009 | `simulate_audience_estimate` | 1 criterion | `audience_size` between 500 and 95000 | ❌ FAIL |
| SB-010 | `simulate_audience_estimate` | 5 criteria | `audience_size` < result of 1 criterion | ❌ FAIL |
| SB-011 | `simulate_audience_estimate` | any valid filter | all required keys present in response | ❌ FAIL |

### 4.2 Parser Unit Tests (`test_parsers.py`)

| Test ID | Function | Input | Expected outcome | Grade on failure |
|---|---|---|---|---|
| PA-001 | `parse_sql_from_response` | valid ` ```sql\nSELECT...\n``` ` | returns raw SQL without fencing | ❌ FAIL |
| PA-002 | `parse_sql_from_response` | no fencing (raw SQL) | returns input stripped | ❌ FAIL |
| PA-003 | `parse_sql_from_response` | empty string | returns empty string | ❌ FAIL |
| PA-004 | `parse_steps_from_response` | 4-step STEP N: format | returns list of 4 dicts | ❌ FAIL |
| PA-005 | `parse_steps_from_response` | each step has `number`, `title`, `body` keys | all keys present | ❌ FAIL |
| PA-006 | `parse_steps_from_response` | malformed (no STEP prefix) | returns empty list, no exception | ❌ FAIL |
| PA-007 | `parse_filter_json_from_response` | valid JSON in response | returns dict with `filters` key | ❌ FAIL |
| PA-008 | `parse_filter_json_from_response` | JSON wrapped in prose | extracts JSON correctly | ❌ FAIL |
| PA-009 | `parse_filter_json_from_response` | invalid JSON | raises or returns safe error dict | ❌ FAIL |

### 4.3 CDP API Integration Tests (`test_cdp_api.py`)

| Test ID | Endpoint | Scenario | Expected HTTP status | Key assertion | Grade on failure |
|---|---|---|---|---|---|
| CDP-001 | `GET /api/cdp/segments` | nominal | 200 | `segments` key is non-empty list | ❌ FAIL |
| CDP-002 | `GET /api/cdp/criteria_fields` | nominal | 200 | `fields` key is non-empty dict | ❌ FAIL |
| CDP-003 | `POST /api/cdp/segment/estimate` | valid simple filter | 200 | `audience_size`, `generated_sql`, `merchant_preview` present | ❌ FAIL |
| CDP-004 | `POST /api/cdp/segment/estimate` | valid complex filter | 200 | `coverage_pct` between 0–100 | ❌ FAIL |
| CDP-005 | `POST /api/cdp/segment/estimate` | empty groups | 400 | `error` key present | ❌ FAIL |
| CDP-006 | `POST /api/cdp/segment/estimate` | missing `filters` key | 400 | `error` key present | ❌ FAIL |
| CDP-007 | `POST /api/cdp/segment/estimate` | unknown field | 400 | error mentions unknown field name | ❌ FAIL |
| CDP-008 | `POST /api/cdp/segment/estimate` | SQL injection value | 400 | request blocked, not executed | ❌ FAIL |
| CDP-009 | `POST /api/cdp/segment/estimate` | `preview_rows=3` | 200 | `len(merchant_preview) == 3` | ❌ FAIL |
| CDP-010 | `POST /api/cdp/segment/estimate` | response time | 200 | response in < 500ms (no Claude call) | ⚠️ WARN |
| CDP-011 | `POST /api/cdp/nl_to_filters` | valid Vietnamese description (mocked) | 200 | `filters` and `mode` keys present | ❌ FAIL |
| CDP-012 | `POST /api/cdp/nl_to_filters` | empty `description` | 400 | `error` key present | ❌ FAIL |
| CDP-013 | `POST /api/cdp/nl_to_filters` | NLP input with special chars `<script>` | 200 or 400 | no raw script in response | ❌ FAIL |

### 4.4 Core API Integration Tests (`test_core_api.py`)

| Test ID | Endpoint | Scenario | Expected HTTP status | Key assertion | Grade on failure |
|---|---|---|---|---|---|
| CORE-001 | `POST /api/translate` | valid Vietnamese question (mocked) | 200 | `sql` and `mode: "translate"` present | ❌ FAIL |
| CORE-002 | `POST /api/translate` | empty `question` field | 400 | `error` key present | ❌ FAIL |
| CORE-003 | `POST /api/translate` | missing `question` key | 400 | `error` key present | ❌ FAIL |
| CORE-004 | `POST /api/explain` | valid SQL input (mocked) | 200 | `steps` list length == 4 | ❌ FAIL |
| CORE-005 | `POST /api/explain` | empty `sql` field | 400 | `error` key present | ❌ FAIL |
| CORE-006 | `POST /api/translate` | Claude raises exception (mocked) | 500 | `error` key present | ❌ FAIL |

### 4.5 Edge Case & Boundary Tests

| Test ID | Category | Scenario | Expected behavior |
|---|---|---|---|
| EDGE-001 | Filter boundary | `between` with `[max, min]` reversed | BLOCK 400 — min must be < max |
| EDGE-002 | Filter boundary | `last consecutive` missing `unit` | BLOCK 400 — unit required |
| EDGE-003 | Filter boundary | string value on numeric field | BLOCK 400 — type mismatch |
| EDGE-004 | Filter boundary | `is one of` with empty array | BLOCK 400 — array must be non-empty |
| EDGE-005 | Filter boundary | 0 criteria in group | BLOCK 400 — structural integrity |
| EDGE-006 | NLP input | 10,000-character description | 400 or graceful truncation — no crash |
| EDGE-007 | NLP input | Vietnamese with emoji `🏪 Tạp hóa > 5tr` | 200 — emoji stripped cleanly |
| EDGE-008 | NLP input | Pure SQL injection `'; DROP TABLE--` | 200 — treated as text, not executed |
| EDGE-009 | Estimate | `preview_rows=0` | 200 — empty `merchant_preview` list |
| EDGE-010 | Estimate | `preview_rows=1000` (exceeds data) | 200 — clamped to available data |
| EDGE-011 | Simulate | 20 criteria (max selectivity) | `audience_size >= 500` (floor enforced) |

---

## 5. EXECUTABLE PYTEST BLUEPRINTS

### 5.1 `tests/test_sql_builder.py`

```python
# tests/test_sql_builder.py
"""
Unit tests for build_sql_from_filters(), estimate_audience_sql(),
and simulate_audience_estimate(). No HTTP, no mocks needed — pure Python.

Install: pip install pytest pytest-asyncio httpx
"""
import pytest
from conftest import (
    build_sql_from_filters,
    estimate_audience_sql,
    simulate_audience_estimate,
)


class TestBuildSqlFromFilters:

    def test_simple_numeric_greater_than(self, simple_filter: dict) -> None:
        sql = build_sql_from_filters(simple_filter)
        assert "50000000" in sql
        assert ">" in sql or "greater" in sql.lower()

    def test_categorical_is_exactly(self) -> None:
        filters = {
            "operator": "AND",
            "groups": [{"operator": "AND", "criteria": [
                {"field": "merchant_region", "operator": "is exactly", "value": "TP. HCM"}
            ]}],
        }
        sql = build_sql_from_filters(filters)
        assert "TP. HCM" in sql

    def test_between_operator(self, between_filter: dict) -> None:
        sql = build_sql_from_filters(between_filter)
        assert "1000000" in sql
        assert "5000000" in sql

    def test_is_one_of_operator(self) -> None:
        filters = {
            "operator": "AND",
            "groups": [{"operator": "AND", "criteria": [
                {"field": "merchant_region", "operator": "is one of",
                 "value": ["TP. HCM", "Hà Nội"]}
            ]}],
        }
        sql = build_sql_from_filters(filters)
        assert "TP. HCM" in sql
        assert "Hà Nội" in sql

    def test_multi_group_and_or(self, complex_filter: dict) -> None:
        sql = build_sql_from_filters(complex_filter)
        assert sql  # non-empty
        assert "AND" in sql.upper() or "OR" in sql.upper()

    def test_unknown_field_raises(self, unknown_field_filter: dict) -> None:
        with pytest.raises((ValueError, KeyError)):
            build_sql_from_filters(unknown_field_filter)


class TestEstimateAudienceSql:

    def test_output_contains_header_comment(self, simple_filter: dict) -> None:
        sql = estimate_audience_sql(simple_filter)
        assert "-- Generated by QueryMind AI CDP" in sql

    def test_output_contains_count_distinct(self, simple_filter: dict) -> None:
        sql = estimate_audience_sql(simple_filter)
        assert "COUNT(DISTINCT m.id)" in sql

    def test_output_is_string(self, simple_filter: dict) -> None:
        result = estimate_audience_sql(simple_filter)
        assert isinstance(result, str)
        assert len(result) > 0


class TestSimulateAudienceEstimate:

    def test_required_keys_present(self, simple_filter: dict) -> None:
        result = simulate_audience_estimate(simple_filter)
        required = {"audience_size", "total_merchants", "coverage_pct",
                    "reach_reliability", "forecasted_conversion", "delta_pct"}
        assert required.issubset(result.keys())

    def test_audience_size_within_bounds(self, simple_filter: dict) -> None:
        result = simulate_audience_estimate(simple_filter)
        assert 500 <= result["audience_size"] <= 95_000

    def test_total_merchants_is_100k(self, simple_filter: dict) -> None:
        assert simulate_audience_estimate(simple_filter)["total_merchants"] == 100_000

    def test_coverage_pct_between_0_and_100(self, simple_filter: dict) -> None:
        pct = simulate_audience_estimate(simple_filter)["coverage_pct"]
        assert 0.0 <= pct <= 100.0

    def test_more_criteria_produces_smaller_audience(self, complex_filter: dict, simple_filter: dict) -> None:
        simple_est   = simulate_audience_estimate(simple_filter)
        complex_est  = simulate_audience_estimate(complex_filter)
        assert complex_est["audience_size"] <= simple_est["audience_size"]

    def test_audience_floor_enforced(self) -> None:
        """20 criteria should still hit the 500-merchant floor, not go to 0."""
        heavy_filter = {
            "operator": "AND",
            "groups": [{"operator": "AND", "criteria": [
                {"field": "gmv_30d", "operator": "greater than", "value": 50_000_000}
            ] * 20}],
        }
        result = simulate_audience_estimate(heavy_filter)
        assert result["audience_size"] >= 500
```

---

### 5.2 `tests/test_parsers.py`

```python
# tests/test_parsers.py
"""Unit tests for all response parser functions."""
import pytest
from local_dev import parse_filter_json_from_response
from app import parse_sql_from_response, parse_steps_from_response  # noqa: F401
# Note: if app.py import fails due to Modal, import via local_dev module instead:
# from conftest import parse_sql_from_response, parse_steps_from_response


class TestParseSqlFromResponse:

    def test_strips_sql_fencing(self, mock_sql_response: str) -> None:
        result = parse_sql_from_response(mock_sql_response)
        assert "```" not in result
        assert result.startswith("--") or result.upper().startswith("SELECT")

    def test_raw_sql_passthrough(self) -> None:
        raw = "SELECT id FROM merchants LIMIT 1"
        assert parse_sql_from_response(raw) == raw

    def test_empty_string(self) -> None:
        assert parse_sql_from_response("") == ""

    def test_strips_leading_trailing_whitespace(self) -> None:
        result = parse_sql_from_response("```sql\n  SELECT 1  \n```")
        assert result == "SELECT 1"


class TestParseStepsFromResponse:

    def test_returns_four_steps(self, mock_steps_response: str) -> None:
        steps = parse_steps_from_response(mock_steps_response)
        assert len(steps) == 4

    def test_each_step_has_required_keys(self, mock_steps_response: str) -> None:
        steps = parse_steps_from_response(mock_steps_response)
        for step in steps:
            assert "number" in step
            assert "title"  in step
            assert "body"   in step

    def test_step_numbers_sequential(self, mock_steps_response: str) -> None:
        steps = parse_steps_from_response(mock_steps_response)
        numbers = [s["number"] for s in steps]
        assert numbers == [1, 2, 3, 4]

    def test_malformed_input_returns_empty_list(self) -> None:
        assert parse_steps_from_response("No steps here at all") == []

    def test_no_exception_on_empty_string(self) -> None:
        result = parse_steps_from_response("")
        assert isinstance(result, list)


class TestParseFilterJsonFromResponse:

    def test_extracts_filters_key(self, mock_filter_json_response: str) -> None:
        result = parse_filter_json_from_response(mock_filter_json_response)
        assert "filters" in result

    def test_filters_has_operator(self, mock_filter_json_response: str) -> None:
        result = parse_filter_json_from_response(mock_filter_json_response)
        assert result["filters"].get("operator") in ("AND", "OR")

    def test_handles_json_wrapped_in_prose(self) -> None:
        response = (
            'Here is the filter:\n'
            '{"filters": {"operator": "AND", "groups": []}, "confidence": 0.9}\n'
            'Hope this helps!'
        )
        result = parse_filter_json_from_response(response)
        assert "filters" in result

    def test_invalid_json_does_not_crash(self) -> None:
        result = parse_filter_json_from_response("this is not json at all")
        assert isinstance(result, dict)
```

---

### 5.3 `tests/test_cdp_api.py`

```python
# tests/test_cdp_api.py
"""
Integration tests for all /api/cdp/* endpoints.
Uses httpx.AsyncClient + ASGITransport — no real network, no DB, no API cost.
call_claude() is patched at the local_dev module level.

Install: pip install pytest pytest-asyncio httpx
"""
import time
import pytest
import httpx
from unittest.mock import patch, MagicMock
import local_dev


@pytest.mark.asyncio
class TestCdpSegmentsEndpoint:

    async def test_returns_200(self, client: httpx.AsyncClient) -> None:
        res = await client.get("/api/cdp/segments")
        assert res.status_code == 200

    async def test_response_has_segments_key(self, client: httpx.AsyncClient) -> None:
        data = (await client.get("/api/cdp/segments")).json()
        assert "segments" in data

    async def test_segments_is_non_empty_list(self, client: httpx.AsyncClient) -> None:
        data = (await client.get("/api/cdp/segments")).json()
        assert isinstance(data["segments"], list)
        assert len(data["segments"]) > 0


@pytest.mark.asyncio
class TestCdpCriteriaFieldsEndpoint:

    async def test_returns_200(self, client: httpx.AsyncClient) -> None:
        res = await client.get("/api/cdp/criteria_fields")
        assert res.status_code == 200

    async def test_response_has_fields_key(self, client: httpx.AsyncClient) -> None:
        data = (await client.get("/api/cdp/criteria_fields")).json()
        assert "fields" in data
        assert isinstance(data["fields"], dict)
        assert len(data["fields"]) > 0


@pytest.mark.asyncio
class TestCdpSegmentEstimateEndpoint:

    async def test_valid_simple_filter_returns_200(
        self, client: httpx.AsyncClient, simple_filter: dict
    ) -> None:
        res = await client.post("/api/cdp/segment/estimate", json={"filters": simple_filter})
        assert res.status_code == 200

    async def test_response_has_required_keys(
        self, client: httpx.AsyncClient, simple_filter: dict
    ) -> None:
        data = (await client.post(
            "/api/cdp/segment/estimate", json={"filters": simple_filter}
        )).json()
        for key in ("audience_size", "generated_sql", "merchant_preview", "mode"):
            assert key in data, f"Missing key: {key}"

    async def test_mode_is_cdp_estimate(
        self, client: httpx.AsyncClient, simple_filter: dict
    ) -> None:
        data = (await client.post(
            "/api/cdp/segment/estimate", json={"filters": simple_filter}
        )).json()
        assert data["mode"] == "cdp_estimate"

    async def test_coverage_pct_valid_range(
        self, client: httpx.AsyncClient, complex_filter: dict
    ) -> None:
        data = (await client.post(
            "/api/cdp/segment/estimate", json={"filters": complex_filter}
        )).json()
        assert 0.0 <= data["coverage_pct"] <= 100.0

    async def test_preview_rows_respected(
        self, client: httpx.AsyncClient, simple_filter: dict
    ) -> None:
        data = (await client.post(
            "/api/cdp/segment/estimate",
            json={"filters": simple_filter, "preview_rows": 3}
        )).json()
        assert len(data["merchant_preview"]) <= 3

    async def test_empty_groups_returns_400(
        self, client: httpx.AsyncClient, empty_groups_filter: dict
    ) -> None:
        res = await client.post(
            "/api/cdp/segment/estimate", json={"filters": empty_groups_filter}
        )
        assert res.status_code == 400
        assert "error" in res.json()

    async def test_missing_filters_key_returns_400(
        self, client: httpx.AsyncClient
    ) -> None:
        res = await client.post("/api/cdp/segment/estimate", json={"segment_name": "test"})
        assert res.status_code == 400

    async def test_unknown_field_returns_400(
        self, client: httpx.AsyncClient, unknown_field_filter: dict
    ) -> None:
        res = await client.post(
            "/api/cdp/segment/estimate", json={"filters": unknown_field_filter}
        )
        assert res.status_code == 400
        assert "error" in res.json()

    async def test_sql_injection_is_blocked(
        self, client: httpx.AsyncClient, sql_injection_filter: dict
    ) -> None:
        res = await client.post(
            "/api/cdp/segment/estimate", json={"filters": sql_injection_filter}
        )
        assert res.status_code in (400, 403)
        body = res.json()
        assert "error" in body
        # Verify the injected payload is not echoed back in generated_sql
        assert "DROP TABLE" not in str(body)

    @pytest.mark.slow
    async def test_response_time_under_500ms(
        self, client: httpx.AsyncClient, simple_filter: dict
    ) -> None:
        """Estimate endpoint must respond in < 500ms (deterministic sim, no Claude call)."""
        start = time.perf_counter()
        await client.post("/api/cdp/segment/estimate", json={"filters": simple_filter})
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert elapsed_ms < 500, f"Response took {elapsed_ms:.1f}ms — exceeds 500ms threshold"


@pytest.mark.asyncio
class TestCdpNlToFiltersEndpoint:

    async def test_valid_description_returns_200(
        self, client: httpx.AsyncClient, mock_filter_json_response: str
    ) -> None:
        with patch.object(local_dev, "call_claude", return_value=mock_filter_json_response):
            res = await client.post(
                "/api/cdp/nl_to_filters",
                json={"description": "Tìm tạp hóa TP HCM có GMV > 50M"}
            )
        assert res.status_code == 200

    async def test_response_has_filters_and_mode(
        self, client: httpx.AsyncClient, mock_filter_json_response: str
    ) -> None:
        with patch.object(local_dev, "call_claude", return_value=mock_filter_json_response):
            data = (await client.post(
                "/api/cdp/nl_to_filters",
                json={"description": "Tìm tạp hóa TP HCM có GMV > 50M"}
            )).json()
        assert "filters" in data
        assert data.get("mode") == "nl_to_filters"

    async def test_empty_description_returns_400(
        self, client: httpx.AsyncClient
    ) -> None:
        res = await client.post("/api/cdp/nl_to_filters", json={"description": ""})
        assert res.status_code == 400
        assert "error" in res.json()

    async def test_missing_description_key_returns_400(
        self, client: httpx.AsyncClient
    ) -> None:
        res = await client.post("/api/cdp/nl_to_filters", json={})
        assert res.status_code == 400

    async def test_xss_input_does_not_crash(
        self, client: httpx.AsyncClient, mock_filter_json_response: str
    ) -> None:
        with patch.object(local_dev, "call_claude", return_value=mock_filter_json_response):
            res = await client.post(
                "/api/cdp/nl_to_filters",
                json={"description": "<script>alert('xss')</script>"}
            )
        assert res.status_code in (200, 400)
        assert "<script>" not in res.text
```

---

### 5.4 `tests/test_core_api.py`

```python
# tests/test_core_api.py
"""Integration tests for /api/translate and /api/explain."""
import pytest
import httpx
from unittest.mock import patch
import local_dev


@pytest.mark.asyncio
class TestTranslateEndpoint:

    async def test_valid_question_returns_200(
        self, client: httpx.AsyncClient, mock_sql_response: str
    ) -> None:
        with patch.object(local_dev, "call_claude", return_value=mock_sql_response):
            res = await client.post(
                "/api/translate",
                json={"question": "Top 10 merchant theo doanh thu"}
            )
        assert res.status_code == 200

    async def test_response_has_sql_and_mode(
        self, client: httpx.AsyncClient, mock_sql_response: str
    ) -> None:
        with patch.object(local_dev, "call_claude", return_value=mock_sql_response):
            data = (await client.post(
                "/api/translate",
                json={"question": "Top 10 merchant theo doanh thu"}
            )).json()
        assert "sql" in data
        assert data["mode"] == "translate"

    async def test_sql_response_has_no_fencing(
        self, client: httpx.AsyncClient, mock_sql_response: str
    ) -> None:
        with patch.object(local_dev, "call_claude", return_value=mock_sql_response):
            data = (await client.post(
                "/api/translate", json={"question": "top merchants"}
            )).json()
        assert "```" not in data["sql"]

    async def test_empty_question_returns_400(self, client: httpx.AsyncClient) -> None:
        res = await client.post("/api/translate", json={"question": ""})
        assert res.status_code == 400

    async def test_missing_question_key_returns_400(self, client: httpx.AsyncClient) -> None:
        res = await client.post("/api/translate", json={})
        assert res.status_code == 400

    async def test_claude_exception_returns_500(self, client: httpx.AsyncClient) -> None:
        with patch.object(local_dev, "call_claude", side_effect=Exception("API unavailable")):
            res = await client.post("/api/translate", json={"question": "test"})
        assert res.status_code == 500
        assert "error" in res.json()


@pytest.mark.asyncio
class TestExplainEndpoint:

    async def test_valid_sql_returns_200(
        self, client: httpx.AsyncClient, mock_steps_response: str
    ) -> None:
        with patch.object(local_dev, "call_claude", return_value=mock_steps_response):
            res = await client.post(
                "/api/explain",
                json={"sql": "SELECT id FROM merchants LIMIT 1"}
            )
        assert res.status_code == 200

    async def test_response_has_exactly_4_steps(
        self, client: httpx.AsyncClient, mock_steps_response: str
    ) -> None:
        with patch.object(local_dev, "call_claude", return_value=mock_steps_response):
            data = (await client.post(
                "/api/explain",
                json={"sql": "SELECT id FROM merchants"}
            )).json()
        assert len(data["steps"]) == 4

    async def test_empty_sql_returns_400(self, client: httpx.AsyncClient) -> None:
        res = await client.post("/api/explain", json={"sql": ""})
        assert res.status_code == 400
```

---

### 5.5 `tests/test_e2e.py` — Real API Suite (Skipped by Default)

```python
# tests/test_e2e.py
"""
End-to-end tests that make real Anthropic API calls.
These are SKIPPED during standard local testing.

To run this suite:
  export ANTHROPIC_API_KEY=sk-ant-api03-...   (bash)
  $env:ANTHROPIC_API_KEY = "sk-ant-api03-..."  (PowerShell)
  pytest tests/test_e2e.py -m e2e -v

WARNING: Running this suite incurs real Anthropic API costs.
Each test makes 1 real API call (~$0.001–$0.01 per test).
"""
import os
import pytest
import httpx


pytestmark = pytest.mark.e2e


@pytest.fixture(autouse=True)
def require_real_api_key() -> None:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key or key.startswith("sk-test-"):
        pytest.skip("Real ANTHROPIC_API_KEY required for e2e tests")


@pytest.mark.asyncio
async def test_translate_real_vietnamese_question(client: httpx.AsyncClient) -> None:
    """Verify Claude produces valid SQL from a real Vietnamese question."""
    res = await client.post(
        "/api/translate",
        json={"question": "Top 10 merchant có tổng doanh thu cao nhất tháng này"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "sql" in data
    assert "SELECT" in data["sql"].upper()
    assert "```" not in data["sql"]


@pytest.mark.asyncio
async def test_explain_real_sql(client: httpx.AsyncClient) -> None:
    """Verify Claude returns 4 structured Vietnamese steps."""
    sql = "SELECT m.name, SUM(t.amount) AS total FROM merchants m JOIN transactions t ON t.merchant_id = m.id WHERE t.status = 'completed' GROUP BY m.name LIMIT 10"
    res = await client.post("/api/explain", json={"sql": sql})
    assert res.status_code == 200
    steps = res.json()["steps"]
    assert len(steps) == 4
    for step in steps:
        assert step["title"]
        assert step["body"]


@pytest.mark.asyncio
async def test_nl_to_filters_real_vietnamese(client: httpx.AsyncClient) -> None:
    """Verify Claude maps a Vietnamese description to a valid filter JSON."""
    res = await client.post(
        "/api/cdp/nl_to_filters",
        json={"description": "Tìm tạp hóa ở TPHCM có GMV > 50M và đã cài app"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "filters" in data
    assert data["filters"].get("operator") in ("AND", "OR")
    groups = data["filters"].get("groups", [])
    assert len(groups) >= 1
```

---

## 6. FRONTEND HEALTH CHECKLIST

The following checks are performed by **manual review or static analysis** since `cdp.html` JS cannot be executed in a pytest context. Flag any violation as ⚠️ WARN in the Code Review report.

| Check | What to verify | Tool |
|---|---|---|
| Debounce present | `triggerEstimate()` uses `clearTimeout + setTimeout(fn, ≥400)` | Static scan |
| No `eval()` | No `eval(`, `new Function(`, or `setTimeout("string")` | Static scan |
| Error boundary on `fetch` | Every `fetch()` call is wrapped in `try/catch` | Static scan |
| `textContent` not `innerHTML` for server data | All `merchant_store`, `region`, `tag` use `.textContent` | Static scan |
| Button disabled during async | `btn.disabled = true` before `await fetch(...)`, restored in `finally` | Static scan |
| No memory leak on row removal | `removeRow()` calls `element.remove()` | Static scan |
| Toast fallback visible on error | `showToast(...)` called in every `catch(e)` block | Static scan |

---

## 7. RUNNING THE TEST SUITE

```powershell
# Standard run — all unit + integration tests, zero API cost
pytest tests/ -v --ignore=tests/test_e2e.py

# Run only unit tests (fastest, no HTTP)
pytest tests/test_sql_builder.py tests/test_parsers.py -v

# Run only integration tests
pytest tests/test_cdp_api.py tests/test_core_api.py -v

# Run with performance threshold check
pytest tests/test_cdp_api.py -v -m slow

# Run e2e suite (requires real API key, incurs cost)
$env:ANTHROPIC_API_KEY = "sk-ant-api03-..."
pytest tests/test_e2e.py -m e2e -v

# Run full suite with coverage report
pytest tests/ --ignore=tests/test_e2e.py --cov=local_dev --cov-report=term-missing
```
