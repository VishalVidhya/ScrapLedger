from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


def make_mock_response(content='{"compliance": "ok"}', prompt_tokens=10, completion_tokens=20):
    mock_resp = MagicMock()
    mock_resp.choices = [
        MagicMock(message=MagicMock(content=content))
    ]
    mock_resp.usage = MagicMock(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
    )
    return mock_resp


def test_chat_success(client: TestClient):
    mock_resp = make_mock_response(content='{"status": "compliant", "penalty": 0}')
    with patch("app.main.completion", return_value=mock_resp), \
         patch("app.main.completion_cost", return_value=0.00015):
        response = client.post("/chat", json={"query": "Check EPR return deadline"})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "response" in data
    assert data["response"]["status"] == "compliant"
    assert data["usage"]["total_tokens"] == 30
    assert data["usage"]["cost_usd"] == 0.00015

    # Check that usage endpoint updated
    usage = client.get("/usage").json()
    assert usage["total_tokens"] >= 30
    assert usage["cost_usd"] >= 0.00015


def test_chat_fallback(client: TestClient):
    """When primary model fails, fallback model should be used."""
    mock_resp = make_mock_response(content='{"source": "fallback_model"}')

    def side_effect(*args, **kwargs):
        if kwargs.get("model") == "gemini/gemini-flash-latest":
            raise RuntimeError("Primary model rate limited")
        return mock_resp

    with patch("app.main.completion", side_effect=side_effect), \
         patch("app.main.completion_cost", return_value=0.0002):
        response = client.post(
            "/chat",
            json={"query": "What are battery waste rules?", "model": "gemini/gemini-flash-latest"}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["model_used"] != "gemini/gemini-flash-latest"


def test_chat_all_models_fail(client: TestClient):
    """When all models in the fallback chain fail, return 503."""
    with patch("app.main.completion", side_effect=RuntimeError("API error")):
        response = client.post("/chat", json={"query": "Hello"})

    assert response.status_code == 503
    assert "All AI models are currently unavailable" in response.json()["detail"]


def test_chat_streaming(client: TestClient):
    """Streaming response returns event stream chunks."""
    chunk1 = MagicMock()
    chunk1.choices = [MagicMock(delta=MagicMock(content="Hello "))]
    chunk2 = MagicMock()
    chunk2.choices = [MagicMock(delta=MagicMock(content="World"))]

    with patch("app.main.completion", return_value=[chunk1, chunk2]):
        response = client.post("/chat", json={"query": "Hello", "stream": True})

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    assert "Hello " in response.text
    assert "World" in response.text
    assert "[DONE]" in response.text
