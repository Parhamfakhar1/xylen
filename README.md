Xylen  
A Minimal, Async-First Python Web Framework for Ultra-Low Latency Applications  

Built for developers who prioritize speed, simplicity, and control, Xylen delivers native ASGI performance with zero external dependencies—pure Python, maximum efficiency, minimal overhead.

Core Features  
• Async-first architecture with full ASGI compliance  
• Sub-millisecond response times and memory footprint under 10MB  
• Type-safe routing: define paths like `/user/{id:int}` and receive validated parameters automatically  
• Built-in security middleware: CORS, CSRF protection, and configurable rate limiting  
• Automatic OpenAPI 3.0 documentation—no Pydantic or extra setup required  
• Dedicated CLI tooling: `xylen run --app myapp:app --reload` for seamless development  
• Full-featured test client for writing reliable, isolated unit tests  
• Zero mandatory dependencies—runs entirely on the Python standard library  

Getting Started  
Install Xylen from PyPI:  
```bash
pip install xylen
```

Create your application (`app.py`):  
```python
from xylen import Xylen

app = Xylen(
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
    return {"message": "Hello from Xylen!"}

@app.openapi(
    path="/user/{user_id:int}",
    methods=["GET"],
    summary="Get user by ID"
)
def get_user(request, user_id: int):
    return {"user_id": user_id}
```

Launch with live reloading:  
```bash
xylen run --app app:app --reload --port 8000
```

Explore your endpoints:  
- Application: http://127.0.0.1:8000/hello  
- Interactive API documentation: http://127.0.0.1:8000/docs  

Testing Your Application  
Xylen includes a production-grade test client for fast, dependency-free testing:  
```python
from app import app
from xylen import TestClient

def test_hello():
    client = TestClient(app)
    resp = client.get("/hello")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Hello from Xylen!"
```

Run the test suite:  
```bash
pip install -e ".[dev]"
pytest
```

Middleware Configuration  
Enable robust defaults out of the box:  
```python
app = Xylen(
    cors=True,
    csrf=True,
    rate_limit=True,
    rate_limit_config={"max_requests": 10, "window_seconds": 60}
)
```

License  
MIT © Parham Fakhari  

Xylen: Lightweight as the wind, fast as lightning.