# tests/test_openapi.py
from zephyr.app import Zephyr
from zephyr.testclient import TestClient

def test_openapi_json():
    app = Zephyr()

    @app.openapi(
        path="/hello",
        methods=["GET"],
        summary="Test endpoint",
        responses={200: {"description": "OK"}}
    )
    def hello(request):
        return {"msg": "hi"}

    client = TestClient(app)
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert data["openapi"] == "3.0.3"
    assert "/hello" in data["paths"]
    assert "get" in data["paths"]["/hello"]

def test_swagger_ui():
    app = Zephyr()
    client = TestClient(app)
    response = client.get("/docs")
    assert response.status_code == 200
    assert b"SwaggerUIBundle" in response._body