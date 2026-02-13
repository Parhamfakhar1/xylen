# zephyrpy/response.py
from typing import Dict, Any

class Response:
    def __init__(self, body: bytes, status_code: int = 200, headers=None):
        self.body = body
        self.status_code = status_code
        if headers is None:
            self.headers = {}
        else:
            self.headers = {
                (k.encode() if isinstance(k, str) else k): 
                (v.encode() if isinstance(v, str) else v)
                for k, v in headers.items()
            }

    async def __call__(self, scope, receive, send):
        await send({
            "type": "http.response.start",
            "status": self.status_code,
            "headers": list(self.headers.items()),
        })
        await send({
            "type": "http.response.body",
            "body": self.body,
        })

class PlainTextResponse(Response):
    def __init__(self, text: str, status_code: int = 200, headers=None):
        final_headers = {"content-type": "text/plain; charset=utf-8"}
        if headers:
            final_headers.update(headers)
        super().__init__(text.encode("utf-8"), status_code, final_headers)

class JSONResponse(Response):
    def __init__(self, data: Dict[Any, Any], status_code: int = 200, headers=None):
        import json
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        final_headers = {"content-type": "application/json; charset=utf-8"}
        if headers:
            final_headers.update(headers)
        super().__init__(body, status_code, final_headers)