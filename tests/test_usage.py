def test_usage_endpoint(client):
    response = client.get("/usage")
    assert response.status_code == 200
    data = response.json()
    assert "total_tokens" in data
    assert "cost_usd" in data
    assert "prompt_tokens" in data
    assert "completion_tokens" in data
    assert isinstance(data["total_tokens"], int)
    assert isinstance(data["cost_usd"], (int, float))
