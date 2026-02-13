# zephyrpy/middleware/csrf.py
import os
import secrets
import hashlib
from ..response import PlainTextResponse

def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)

def hash_token(token: str, secret: str) -> str:
    return hashlib.sha256((token + secret).encode()).hexdigest()

class CSRFMiddleware:
    def __init__(self, app, secret_key: str = None, cookie_name: str = "csrftoken", header_name: str = "X-CSRF-Token"):
        self.app = app
        self.secret_key = secret_key or os.getenv("zephyrpy_SECRET_KEY") or generate_csrf_token()
        self.cookie_name = cookie_name
        self.header_name = header_name.lower().replace("-", "_")

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        method = scope["method"]
        headers = dict(scope.get("headers", []))
        cookies_raw = headers.get(b"cookie", b"").decode()
        cookies = {}
        for pair in cookies_raw.split(";"):
            if "=" in pair:
                k, v = pair.strip().split("=", 1)
                cookies[k] = v

        csrf_token = cookies.get(self.cookie_name)
        if not csrf_token:
            csrf_token = generate_csrf_token()

        if method in ("GET", "HEAD", "OPTIONS", "TRACE"):
            pass
        else:
            expected_hash = hash_token(csrf_token, self.secret_key)
            submitted_token = None
            header_key = self.header_name.encode()
            if header_key in headers:
                submitted_token = headers[header_key].decode()

            if not submitted_token or hash_token(submitted_token, self.secret_key) != expected_hash:
                return await self._send_error(send, "CSRF token missing or invalid")

        async def wrapped_send(event):
            if event["type"] == "http.response.start":
                has_cookie = any(
                    h[0].decode() == "set-cookie" and self.cookie_name in h[1].decode()
                    for h in event.get("headers", [])
                )
                if not has_cookie:
                    cookie_value = f"{self.cookie_name}={csrf_token}; Path=/; SameSite=Lax; HttpOnly"
                    event["headers"] = list(event.get("headers", [])) + [(b"set-cookie", cookie_value.encode())]
            await send(event)

        await self.app(scope, receive, wrapped_send)

    async def _send_error(self, send, message: str):
        response = PlainTextResponse(message, status_code=403)
        await response({}, None, send)