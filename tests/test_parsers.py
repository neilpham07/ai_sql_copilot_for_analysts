"""
Unit tests for all response parser functions.
Test IDs: PA-001 through PA-009
"""
import pytest
from conftest import (
    parse_sql_from_response,
    parse_steps_from_response,
    parse_filter_json_from_response,
)


class TestParseSqlFromResponse:

    def test_pa001_strips_sql_fencing(self, mock_sql_response: str) -> None:
        result = parse_sql_from_response(mock_sql_response)
        assert "```" not in result
        assert result.upper().startswith("--") or result.upper().startswith("SELECT")

    def test_pa002_raw_sql_passthrough(self) -> None:
        raw = "SELECT id FROM merchants LIMIT 1"
        assert parse_sql_from_response(raw) == raw

    def test_pa003_empty_string(self) -> None:
        assert parse_sql_from_response("") == ""

    def test_pa004_strips_leading_trailing_whitespace(self) -> None:
        result = parse_sql_from_response("```sql\n  SELECT 1  \n```")
        assert result == "SELECT 1"

    def test_pa005_multiline_sql_preserved(self) -> None:
        sql = "SELECT m.name\nFROM merchants m\nLIMIT 5"
        result = parse_sql_from_response(f"```sql\n{sql}\n```")
        assert "FROM merchants m" in result


class TestParseStepsFromResponse:

    def test_pa006_returns_four_steps(self, mock_steps_response: str) -> None:
        steps = parse_steps_from_response(mock_steps_response)
        assert len(steps) == 4

    def test_pa007_each_step_has_required_keys(self, mock_steps_response: str) -> None:
        steps = parse_steps_from_response(mock_steps_response)
        for step in steps:
            assert "number" in step
            assert "title"  in step
            assert "body"   in step

    def test_pa008_step_numbers_sequential(self, mock_steps_response: str) -> None:
        steps = parse_steps_from_response(mock_steps_response)
        assert [s["number"] for s in steps] == [1, 2, 3, 4]

    def test_pa009_malformed_input_returns_empty_list(self) -> None:
        assert parse_steps_from_response("No steps here at all") == []

    def test_pa010_no_exception_on_empty_string(self) -> None:
        result = parse_steps_from_response("")
        assert isinstance(result, list)

    def test_pa011_step_titles_nonempty(self, mock_steps_response: str) -> None:
        steps = parse_steps_from_response(mock_steps_response)
        for step in steps:
            assert len(step["title"]) > 0


class TestParseFilterJsonFromResponse:

    def test_pa012_extracts_filters_key(self, mock_filter_json_response: str) -> None:
        result = parse_filter_json_from_response(mock_filter_json_response)
        assert "filters" in result

    def test_pa013_filters_has_operator(self, mock_filter_json_response: str) -> None:
        result = parse_filter_json_from_response(mock_filter_json_response)
        assert result["filters"].get("operator") in ("AND", "OR")

    def test_pa014_handles_json_wrapped_in_prose(self) -> None:
        response = (
            "Here is the filter:\n"
            '{"filters": {"operator": "AND", "groups": []}, "confidence": 0.9}\n'
            "Hope this helps!"
        )
        result = parse_filter_json_from_response(response)
        assert "filters" in result

    def test_pa015_invalid_json_raises_or_returns_safe(self) -> None:
        """Implementation may raise ValueError or return a safe fallback dict."""
        try:
            result = parse_filter_json_from_response("this is not json at all")
            assert isinstance(result, dict)
        except (ValueError, KeyError):
            pass  # raising is acceptable per spec
