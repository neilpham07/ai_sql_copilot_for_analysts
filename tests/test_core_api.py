"""
Integration tests for /api/translate and /api/explain.
call_gemini() is patched at the local_dev module level — zero API cost.

Test IDs: CORE-001 through CORE-006
"""
import pytest
import httpx
from unittest.mock import patch
import local_dev


@pytest.mark.asyncio
class TestTranslateEndpoint:

    async def test_core001_valid_question_returns_200(
        self, client: httpx.AsyncClient, mock_sql_response: str
    ) -> None:
        with patch.object(local_dev, "call_gemini", return_value=mock_sql_response):
            res = await client.post(
                "/api/translate",
                json={"question": "Top 10 merchant theo doanh thu"}
            )
        assert res.status_code == 200

    async def test_core001_response_has_sql_and_mode(
        self, client: httpx.AsyncClient, mock_sql_response: str
    ) -> None:
        with patch.object(local_dev, "call_gemini", return_value=mock_sql_response):
            data = (await client.post(
                "/api/translate",
                json={"question": "Top 10 merchant theo doanh thu"}
            )).json()
        assert "sql" in data
        assert data["mode"] == "translate"

    async def test_core001_sql_has_no_markdown_fencing(
        self, client: httpx.AsyncClient, mock_sql_response: str
    ) -> None:
        with patch.object(local_dev, "call_gemini", return_value=mock_sql_response):
            data = (await client.post(
                "/api/translate", json={"question": "top merchants"}
            )).json()
        assert "```" not in data["sql"]

    async def test_core002_empty_question_returns_400(
        self, client: httpx.AsyncClient
    ) -> None:
        res = await client.post("/api/translate", json={"question": ""})
        assert res.status_code == 400
        assert "error" in res.json()

    async def test_core003_missing_question_key_returns_400(
        self, client: httpx.AsyncClient
    ) -> None:
        res = await client.post("/api/translate", json={})
        assert res.status_code == 400
        assert "error" in res.json()

    async def test_core006_claude_exception_returns_500(
        self, client: httpx.AsyncClient
    ) -> None:
        with patch.object(local_dev, "call_gemini", side_effect=Exception("API unavailable")):
            res = await client.post("/api/translate", json={"question": "test"})
        assert res.status_code == 500
        assert "error" in res.json()


@pytest.mark.asyncio
class TestExplainEndpoint:

    async def test_core004_valid_sql_returns_200(
        self, client: httpx.AsyncClient, mock_steps_response: str
    ) -> None:
        with patch.object(local_dev, "call_gemini", return_value=mock_steps_response):
            res = await client.post(
                "/api/explain",
                json={"sql": "SELECT id FROM merchants LIMIT 1"}
            )
        assert res.status_code == 200

    async def test_core004_response_has_exactly_4_steps(
        self, client: httpx.AsyncClient, mock_steps_response: str
    ) -> None:
        with patch.object(local_dev, "call_gemini", return_value=mock_steps_response):
            data = (await client.post(
                "/api/explain",
                json={"sql": "SELECT id FROM merchants"}
            )).json()
        assert len(data["steps"]) == 4

    async def test_core004_mode_is_explain(
        self, client: httpx.AsyncClient, mock_steps_response: str
    ) -> None:
        with patch.object(local_dev, "call_gemini", return_value=mock_steps_response):
            data = (await client.post(
                "/api/explain",
                json={"sql": "SELECT id FROM merchants"}
            )).json()
        assert data["mode"] == "explain"

    async def test_core005_empty_sql_returns_400(
        self, client: httpx.AsyncClient
    ) -> None:
        res = await client.post("/api/explain", json={"sql": ""})
        assert res.status_code == 400
        assert "error" in res.json()

    async def test_core005_missing_sql_key_returns_400(
        self, client: httpx.AsyncClient
    ) -> None:
        res = await client.post("/api/explain", json={})
        assert res.status_code == 400
        assert "error" in res.json()
