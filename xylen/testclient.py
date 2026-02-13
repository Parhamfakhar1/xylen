# Xylen/testclient.py
import json
from urllib.parse import urlencode
from .response import Response

class TestClient:
    def __init__(self, app):
        # Use the full ASGI app chain (with middleware)
        self.app = getattr(app, '_asgi_app', app)

    def _build_scope(self, method, path, headers=None, query_params=None):
        if query_params:
            query_string = urlencode(query_params).encode()
        else:
            query_string = b""

        if headers is None:
            headers = {}
        header_list = [(k.encode(), v.encode()) for k, v in headers.items()]

        return {
            "type": "http",
            "method": method.upper(),
            "path": path.split("?")[0],
            "query_string": query_string,
            "headers": header_list,
            "client": ("127.0.0.1", 80),
            "scheme": "http",
        }

    async def _make_request(self, method, path, headers=None, json_data=None, query_params=None):
        scope = self._build_scope(method, path, headers, query_params)
        sent = []

        async def receive():
            body = json.dumps(json_data).encode() if json_data else b""
            return {"type": "http.request", "body": body}

        async def send(event):
            sent.append(event)

        try:
            await self.app(scope, receive, send)
        except Exception as e:
            return TestResponse(status_code=500, body=str(e).encode(), headers={})

        start_event = next((e for e in sent if e["type"] == "http.response.start"), None)
        body_event = next((e for e in sent if e["type"] == "http.response.body"), None)

        if not start_event or not body_event:
            return TestResponse(status_code=500, body=b"", headers={})

        status_code = start_event["status"]
        headers = dict(start_event.get("headers", []))
        body = body_event.get("body", b"")

        return TestResponse(status_code=status_code, body=body, headers=headers)

    def get(self, path, headers=None, query_params=None):
        import asyncio
        return asyncio.run(self._make_request("GET", path, headers, None, query_params))

    def post(self, path, json=None, headers=None):
        import asyncio
        return asyncio.run(self._make_request("POST", path, headers, json_data=json))


class TestResponse:
    def __init__(self, status_code, body, headers):
        self.status_code = status_code
        self._body = body
        self.headers = {k.decode(): v.decode() for k, v in headers.items()} if headers else {}

    @property
    def text(self):
        return self._body.decode("utf-8")

    def json(self):
        return json.loads(self._body.decode("utf-8"))