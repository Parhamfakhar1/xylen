# zephyr/middleware/cors.py
class CORSMiddleware:
    def __init__(
        self,
        app,
        allow_origins=None,
        allow_methods=None,
        allow_headers=None,
    ):
        self.app = app
        self.allow_origins = set(allow_origins or ["*"])
        self.allow_methods = set(m.upper() for m in (allow_methods or ["*"]))
        self.allow_headers = set(h.lower() for h in (allow_headers or ["*"]))

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        method = scope["method"]
        headers = dict(scope.get("headers", []))
        origin = headers.get(b"origin", b"").decode()

        # Build CORS headers once
        cors_headers = self._build_cors_headers(origin)

        if method == "OPTIONS":
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": list(cors_headers.items()),
                }
            )
            await send({"type": "http.response.body", "body": b""})
            return

        # Wrap send to inject CORS headers for ALL methods
        async def wrapped_send(event):
            if event["type"] == "http.response.start":
                existing = dict(event.get("headers", []))
                existing.update(cors_headers)
                event["headers"] = list(existing.items())
            await send(event)

        await self.app(scope, receive, wrapped_send)

    def _build_cors_headers(self, origin: str):
        headers = {}

        if "*" in self.allow_origins or origin in self.allow_origins:
            headers[b"access-control-allow-origin"] = (
                origin.encode() if origin else b"*"
            )

        if "*" in self.allow_methods:
            headers[b"access-control-allow-methods"] = (
                b"GET, POST, PUT, PATCH, DELETE, OPTIONS"
            )
        else:
            methods = ", ".join(sorted(self.allow_methods))
            headers[b"access-control-allow-methods"] = methods.encode()

        if "*" in self.allow_headers:
            headers[b"access-control-allow-headers"] = b"*"
        else:
            headers[b"access-control-allow-headers"] = ", ".join(
                sorted(self.allow_headers)
            ).encode()

        return headers
