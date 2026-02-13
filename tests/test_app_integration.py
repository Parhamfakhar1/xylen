# tests/test_app_integration.py
from zephyrpy import zephyrpy, TestClient

def test_full_app():
    app = zephyrpy(
        cors=True,
        cors_config={"allow_origins": ["*"]},
        rate_limit=False
    )

    @app.openapi(
        path="/user/{uid:int}",
        methods=["GET"],
        summary="Get user",
        responses={200: {"description": "User found"}}
    )
    async def get_user(request, uid: int):
        return {"id": uid, "name": "Test"}

    client = TestClient(app)

    # Test valid route
    resp = client.get("/user/42", headers={"Origin": "http://localhost:3000"})
    assert resp.status_code == 200
    assert resp.json()["id"] == 42
    assert "access-control-allow-origin" in resp.headers 