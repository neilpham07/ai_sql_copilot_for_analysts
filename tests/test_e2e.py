"""
End-to-end tests that make real Google Gemini API calls.
SKIPPED during standard local testing — only run when real key is present.

To run this suite:
    $env:GEMINI_API_KEY = "AIza..."  # PowerShell
    pytest tests/test_e2e.py -m e2e -v

WARNING: Each test incurs real Gemini API cost (Free Tier available — check Google AI Studio quota).
"""
import os
import pytest
import httpx


pytestmark = pytest.mark.e2e


@pytest.fixture(autouse=True)
def require_real_api_key() -> None:
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key or key.startswith("test-"):
        pytest.skip("Real GEMINI_API_KEY required for e2e tests")


@pytest.mark.asyncio
async def test_e2e_translate_real_vietnamese_question(client: httpx.AsyncClient) -> None:
    """Gemini produces valid SQL from a real Vietnamese question."""
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
async def test_e2e_explain_real_sql(client: httpx.AsyncClient) -> None:
    """Gemini returns exactly 4 structured Vietnamese steps."""
    sql = (
        "SELECT m.name, SUM(t.amount) AS total "
        "FROM merchants m "
        "JOIN transactions t ON t.merchant_id = m.id "
        "WHERE t.status = 'completed' "
        "GROUP BY m.name "
        "LIMIT 10"
    )
    res = await client.post("/api/explain", json={"sql": sql})
    assert res.status_code == 200
    steps = res.json()["steps"]
    assert len(steps) == 4
    for step in steps:
        assert step["title"]
        assert step["body"]


@pytest.mark.asyncio
async def test_e2e_nl_to_filters_real_vietnamese(client: httpx.AsyncClient) -> None:
    """Gemini maps a Vietnamese description to a valid filter JSON."""
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
