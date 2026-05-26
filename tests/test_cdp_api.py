"""
Integration tests for all /api/cdp/* endpoints.
Uses httpx.AsyncClient + ASGITransport — no real network, no DB, no API cost.
call_gemini() is patched at the local_dev module level for NLP endpoint.

Test IDs: CDP-001 through CDP-013
"""
import time
import pytest
import httpx
from unittest.mock import patch
import local_dev


@pytest.mark.asyncio
class TestCdpSegmentsEndpoint:

    async def test_cdp001_returns_200(self, client: httpx.AsyncClient) -> None:
        res = await client.get("/api/cdp/segments")
        assert res.status_code == 200

    async def test_cdp001_response_has_segments_key(self, client: httpx.AsyncClient) -> None:
        data = (await client.get("/api/cdp/segments")).json()
        assert "segments" in data

    async def test_cdp001_segments_is_non_empty_list(self, client: httpx.AsyncClient) -> None:
        data = (await client.get("/api/cdp/segments")).json()
        assert isinstance(data["segments"], list)
        assert len(data["segments"]) > 0


@pytest.mark.asyncio
class TestCdpCriteriaFieldsEndpoint:

    async def test_cdp002_returns_200(self, client: httpx.AsyncClient) -> None:
        res = await client.get("/api/cdp/criteria_fields")
        assert res.status_code == 200

    async def test_cdp002_response_has_fields_key(self, client: httpx.AsyncClient) -> None:
        data = (await client.get("/api/cdp/criteria_fields")).json()
        assert "fields" in data
        assert isinstance(data["fields"], dict)
        assert len(data["fields"]) > 0


@pytest.mark.asyncio
class TestCdpSegmentEstimateEndpoint:

    async def test_cdp003_valid_simple_filter_returns_200(
        self, client: httpx.AsyncClient, simple_filter: dict
    ) -> None:
        res = await client.post("/api/cdp/segment/estimate", json={"filters": simple_filter})
        assert res.status_code == 200

    async def test_cdp003_response_has_required_keys(
        self, client: httpx.AsyncClient, simple_filter: dict
    ) -> None:
        data = (await client.post(
            "/api/cdp/segment/estimate", json={"filters": simple_filter}
        )).json()
        for key in ("audience_size", "generated_sql", "merchant_preview", "mode"):
            assert key in data, f"Missing key: {key}"

    async def test_cdp003_mode_is_cdp_estimate(
        self, client: httpx.AsyncClient, simple_filter: dict
    ) -> None:
        data = (await client.post(
            "/api/cdp/segment/estimate", json={"filters": simple_filter}
        )).json()
        assert data["mode"] == "cdp_estimate"

    async def test_cdp004_coverage_pct_valid_range(
        self, client: httpx.AsyncClient, complex_filter: dict
    ) -> None:
        data = (await client.post(
            "/api/cdp/segment/estimate", json={"filters": complex_filter}
        )).json()
        assert 0.0 <= data["coverage_pct"] <= 100.0

    async def test_cdp009_preview_rows_respected(
        self, client: httpx.AsyncClient, simple_filter: dict
    ) -> None:
        data = (await client.post(
            "/api/cdp/segment/estimate",
            json={"filters": simple_filter, "preview_rows": 3}
        )).json()
        assert len(data["merchant_preview"]) <= 3

    async def test_cdp005_empty_groups_returns_400(
        self, client: httpx.AsyncClient, empty_groups_filter: dict
    ) -> None:
        res = await client.post(
            "/api/cdp/segment/estimate", json={"filters": empty_groups_filter}
        )
        assert res.status_code == 400
        assert "error" in res.json()

    async def test_cdp006_missing_filters_key_returns_400(
        self, client: httpx.AsyncClient
    ) -> None:
        res = await client.post("/api/cdp/segment/estimate", json={"segment_name": "test"})
        assert res.status_code == 400
        assert "error" in res.json()

    async def test_cdp007_unknown_field_returns_400(
        self, client: httpx.AsyncClient, unknown_field_filter: dict
    ) -> None:
        res = await client.post(
            "/api/cdp/segment/estimate", json={"filters": unknown_field_filter}
        )
        assert res.status_code == 400
        assert "error" in res.json()

    async def test_cdp008_sql_injection_is_blocked(
        self, client: httpx.AsyncClient, sql_injection_filter: dict
    ) -> None:
        res = await client.post(
            "/api/cdp/segment/estimate", json={"filters": sql_injection_filter}
        )
        assert res.status_code in (400, 403)
        body = res.json()
        assert "error" in body
        assert "DROP TABLE" not in str(body)

    @pytest.mark.slow
    async def test_cdp010_response_time_under_500ms(
        self, client: httpx.AsyncClient, simple_filter: dict
    ) -> None:
        """Estimate endpoint must respond in < 500ms — no Claude call involved."""
        start = time.perf_counter()
        await client.post("/api/cdp/segment/estimate", json={"filters": simple_filter})
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert elapsed_ms < 500, f"Response took {elapsed_ms:.1f}ms — exceeds 500ms threshold"


@pytest.mark.asyncio
class TestCdpNlToFiltersEndpoint:

    async def test_cdp011_valid_description_returns_200(
        self, client: httpx.AsyncClient, mock_filter_json_response: str
    ) -> None:
        with patch.object(local_dev, "call_gemini", return_value=mock_filter_json_response):
            res = await client.post(
                "/api/cdp/nl_to_filters",
                json={"description": "Tìm tạp hóa TP HCM có GMV > 50M"}
            )
        assert res.status_code == 200

    async def test_cdp011_response_has_filters_and_mode(
        self, client: httpx.AsyncClient, mock_filter_json_response: str
    ) -> None:
        with patch.object(local_dev, "call_gemini", return_value=mock_filter_json_response):
            data = (await client.post(
                "/api/cdp/nl_to_filters",
                json={"description": "Tìm tạp hóa TP HCM có GMV > 50M"}
            )).json()
        assert "filters" in data
        assert data.get("mode") == "nl_to_filters"

    async def test_cdp012_empty_description_returns_400(
        self, client: httpx.AsyncClient
    ) -> None:
        res = await client.post("/api/cdp/nl_to_filters", json={"description": ""})
        assert res.status_code == 400
        assert "error" in res.json()

    async def test_cdp012_missing_description_key_returns_400(
        self, client: httpx.AsyncClient
    ) -> None:
        res = await client.post("/api/cdp/nl_to_filters", json={})
        assert res.status_code == 400

    async def test_cdp013_xss_input_does_not_echo_script_tag(
        self, client: httpx.AsyncClient, mock_filter_json_response: str
    ) -> None:
        with patch.object(local_dev, "call_gemini", return_value=mock_filter_json_response):
            res = await client.post(
                "/api/cdp/nl_to_filters",
                json={"description": "<script>alert('xss')</script>"}
            )
        assert res.status_code in (200, 400)
        assert "<script>" not in res.text
