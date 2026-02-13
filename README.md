# zephyrpy

A minimal, async-first Python web framework with ultra-low latency and low memory usage.

## ✨ Features


- **Async-first** with ASGI native support  
- **Ultra-low latency** and **minimal RAM usage**  
- **Smart routing** with type-safe path parameters (`/user/{id:int}`)  
- Built-in **CORS**, **CSRF**, and **rate-limiting** middleware  
- Automatic **OpenAPI/Swagger UI** (no Pydantic required)  
- Dedicated CLI: `zephyrpy run --app myapp:app --reload`  
- Full **test client** for unit testing  
- Zero required dependencies — pure Python  

## 🚀 Quick Start

```bash
pip install zephyrpy
```

Create `app.py`:

```python
from zephyrpy import zephyrpy

app = zephyrpy(
    cors=True,
    rate_limit=True,
    rate_limit_config={"max_requests": 100, "window_seconds": 60}
)

@app.openapi(
    path="/hello",
    methods=["GET"],
    summary="Say hello",
    responses={200: {"description": "A greeting message"}}
)
async def hello(request):
    return {"message": "Hello from zephyrpy!"}

@app.openapi(
    path="/user/{user_id:int}",
    methods=["GET"],
    summary="Get user by ID"
)
def get_user(request, user_id: int):
    return {"user_id": user_id}
```

Run with auto-reload:

```bash
zephyrpy run --app app:app --reload --port 8000
```

Visit:
- http://127.0.0.1:8000/hello  
- http://127.0.0.1:8000/docs → Interactive API docs  

## 🧪 Testing

```python
from app import app
from zephyrpy import TestClient

def test_hello():
    client = TestClient(app)
    resp = client.get("/hello")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Hello from zephyrpy!"
```

Run tests:

```bash
pip install -e ".[dev]"
pytest
```

## 📦 Middleware

Enable built-in security and control:

```python
app = zephyrpy(
    cors=True,
    csrf=True,
    rate_limit=True,
    rate_limit_config={"max_requests": 10, "window_seconds": 60}
)
```

## 📄 License

MIT © Parham Fakhari

---

> **zephyrpy**: Lightweight as the wind, fast as lightning.