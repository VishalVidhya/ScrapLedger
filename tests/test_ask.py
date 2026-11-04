from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


def make_mock_response(
    content="Compliance is required under Rule 4.",
    prompt_tokens=25,
    completion_tokens=35,
):
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock(message=MagicMock(content=content))]
    mock_resp.usage = MagicMock(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
    )
    return mock_resp


def test_ask_endpoint_success(client: TestClient):
    mock_answer = (
        "Operating without EPR registration attracts Environmental Compensation charges "
        "and potential closure notices under Battery Waste Management Rules 2022."
    )
    mock_resp = make_mock_response(content=mock_answer, prompt_tokens=50, completion_tokens=30)

    with (
        patch("app.main.completion", return_value=mock_resp),
        patch("app.main.completion_cost", return_value=0.00008),
    ):
        response = client.post(
            "/ask",
            json={
                "query": "What is the penalty for selling batteries without EPR registration?",
                "top_k": 3,
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "What is the penalty for selling batteries without EPR registration?"
    assert data["answer"] == mock_answer
    assert "citations" in data
    assert isinstance(data["citations"], list)
    assert len(data["citations"]) > 0

    # Validate citation structure
    first_citation = data["citations"][0]
    assert "document" in first_citation
    assert "page" in first_citation
    assert isinstance(first_citation["page"], int)
    assert first_citation["page"] >= 1
    assert "section" in first_citation

    # Validate usage metrics
    assert data["usage"]["prompt_tokens"] == 50
    assert data["usage"]["completion_tokens"] == 30
    assert data["usage"]["total_tokens"] == 80
    assert data["usage"]["cost_usd"] == 0.00008

    # Verify cumulative /usage updated
    usage = client.get("/usage").json()
    assert usage["total_tokens"] >= 80
    assert usage["total_calls"] >= 1


def test_ask_endpoint_fallback(client: TestClient):
    mock_resp = make_mock_response(content="Fallback answer citing page 12.")

    def side_effect(*args, **kwargs):
        if kwargs.get("model") == "gemini/gemini-flash-latest":
            raise RuntimeError("API timeout")
        return mock_resp

    with (
        patch("app.main.completion", side_effect=side_effect),
        patch("app.main.completion_cost", return_value=0.00005),
    ):
        response = client.post(
            "/ask",
            json={"query": "What are e-waste collection targets for 2026?", "top_k": 2},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Fallback answer citing page 12."
    assert len(data["citations"]) > 0


def test_ask_all_models_fail(client: TestClient):
    with patch("app.main.completion", side_effect=RuntimeError("All APIs down")):
        response = client.post(
            "/ask",
            json={"query": "Test query"},
        )
    assert response.status_code == 503
    assert response.json()["detail"] == "All AI models are currently unavailable."
