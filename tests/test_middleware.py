# tests/test_middleware.py
import pytest
from zephyrpy.app import zephyrpy
from zephyrpy.testclient import TestClient

def test_cors_middleware():
    app = zephyrpy(cors=True, cors_config={"allow_origins": ["*"]})
    
    @app.route("/test", methods=["GET"])
    def handler(request):
        return {"ok": True}

    client = TestClient(app)
    response = client.get("/test", headers={"Origin": "https://example.com"})
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


def test_rate_limiting(monkeypatch):
    # Mock time to simulate multiple requests over time
    from zephyrpy.middleware.rate_limit import RateLimitMiddleware
    times = iter([1000.0, 1000.1, 1000.2])
    monkeypatch.setattr("zephyrpy.middleware.rate_limit.time.time", lambda: next(times))

    app = zephyrpy(rate_limit=True, rate_limit_config={"max_requests": 2, "window_seconds": 10})

    @app.route("/limited", methods=["GET"])
    def handler(request):
        return {"count": "ok"}

    client = TestClient(app)
    assert client.get("/limited").status_code == 200
    assert client.get("/limited").status_code == 200
    assert client.get("/limited").status_code == 429