"""Unit tests for the AI generate-and-verify workflow with mocked LLM."""

import pytest

from app.errors import LLMTimeoutError
from app.llm.verify_loop import generate_verified_suggestions
from app.schemas import RewriteRequest


@pytest.mark.asyncio
async def test_valid_candidate_accepted(mock_llm_client):
    # Candidate "साथ रहेगा नूर" has exactly 11 matras
    client = mock_llm_client(
        response_data={"candidates": [{"line": "साथ रहेगा नूर", "note": "Drops 'फिर'"}]}
    )
    req = RewriteRequest(
        original_line="साथ रहेगा फिर नूर",
        target_matra_count=11,
        selected_meter="doha",
        charan_index=1,
    )
    resp = await generate_verified_suggestions(req, client=client)
    assert len(resp.suggestions) == 1
    assert resp.suggestions[0].suggested_line == "साथ रहेगा नूर"
    assert resp.suggestions[0].calculated_matra_count == 11
    assert resp.suggestions[0].verified_status is True


@pytest.mark.asyncio
async def test_invalid_candidate_strictly_rejected(mock_llm_client):
    # Candidate "साथ रहेगा फिर नूर" has 13 matras, target is 11
    client = mock_llm_client(
        response_data={
            "candidates": [{"line": "साथ रहेगा फिर नूर", "note": "Unchanged broken candidate"}]
        }
    )
    req = RewriteRequest(
        original_line="साथ रहेगा फिर नूर",
        target_matra_count=11,
        selected_meter="doha",
        charan_index=1,
    )
    resp = await generate_verified_suggestions(req, client=client)
    # MUST BE REJECTED!
    assert len(resp.suggestions) == 0
    assert "No verified rewrite found" in resp.message


@pytest.mark.asyncio
async def test_mixed_candidates_filtered_strictly(mock_llm_client):
    # 1st candidate is invalid (13 matras), 2nd is valid (11 matras: "साथ रहे फिर नूर"), 3rd is invalid
    client = mock_llm_client(
        response_data={
            "candidates": [
                {"line": "साथ रहेगा फिर नूर", "note": "13 matras (invalid)"},
                {"line": "साथ रहे फिर नूर", "note": "11 matras (valid)"},
                {"line": "साथ रहेगा और भी नूर", "note": "15 matras (invalid)"},
            ]
        }
    )
    req = RewriteRequest(
        original_line="साथ रहेगा फिर नूर",
        target_matra_count=11,
        selected_meter="doha",
        charan_index=1,
    )
    resp = await generate_verified_suggestions(req, client=client)
    assert len(resp.suggestions) == 1
    assert resp.suggestions[0].suggested_line == "साथ रहे फिर नूर"
    assert resp.suggestions[0].calculated_matra_count == 11


@pytest.mark.asyncio
async def test_duplicates_removed(mock_llm_client):
    # Duplicate valid lines returned
    client = mock_llm_client(
        response_data={
            "candidates": [
                {"line": "साथ रहेगा नूर", "note": "Attempt 1"},
                {"line": "साथ रहेगा नूर", "note": "Duplicate"},
            ]
        }
    )
    req = RewriteRequest(
        original_line="साथ रहेगा फिर नूर",
        target_matra_count=11,
        selected_meter="doha",
        charan_index=1,
    )
    resp = await generate_verified_suggestions(req, client=client)
    assert len(resp.suggestions) == 1


@pytest.mark.asyncio
async def test_retry_cap_respected(mock_llm_client):
    # Only invalid candidates returned; loop should retry up to MAX_RETRIES then stop gracefully
    client = mock_llm_client(
        response_data={"candidates": [{"line": "साथ रहेगा बहुत ज्यादा नूर", "note": "Broken"}]}
    )
    req = RewriteRequest(
        original_line="साथ रहेगा फिर नूर",
        target_matra_count=11,
        selected_meter="doha",
        charan_index=1,
    )
    resp = await generate_verified_suggestions(req, client=client)
    assert len(resp.suggestions) == 0
    assert resp.attempts_made > 0


@pytest.mark.asyncio
async def test_llm_timeout_handled(mock_llm_client):
    client = mock_llm_client(should_timeout=True)
    req = RewriteRequest(
        original_line="साथ रहेगा फिर नूर",
        target_matra_count=11,
        selected_meter="doha",
        charan_index=1,
    )
    with pytest.raises(LLMTimeoutError):
        await generate_verified_suggestions(req, client=client)


@pytest.mark.asyncio
async def test_malformed_or_empty_json_handled(mock_llm_client):
    # Missing 'candidates' key or non-list structure
    client = mock_llm_client(response_data={"unexpected_key": "some text"})
    req = RewriteRequest(
        original_line="साथ रहेगा फिर नूर",
        target_matra_count=11,
        selected_meter="doha",
        charan_index=1,
    )
    resp = await generate_verified_suggestions(req, client=client)
    assert len(resp.suggestions) == 0
    assert "No verified rewrite found" in resp.message


@pytest.mark.asyncio
async def test_never_trust_llm_self_reported_count(mock_llm_client):
    # Candidate falsely claims in note that it is 11 matras, but text has 13
    client = mock_llm_client(
        response_data={
            "candidates": [
                {
                    "line": "साथ रहेगा फिर नूर",
                    "note": "AI claims: Exactly 11 matras",
                }
            ]
        }
    )
    req = RewriteRequest(
        original_line="साथ रहेगा फिर नूर",
        target_matra_count=11,
        selected_meter="doha",
        charan_index=1,
    )
    resp = await generate_verified_suggestions(req, client=client)
    # Must be strictly rejected by the deterministic engine
    assert len(resp.suggestions) == 0
