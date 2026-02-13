# zephyrpy/app.py
import asyncio
import os
from typing import Callable, Dict, Any, Optional
from .router import Router
from .request import Request
from .response import Response, PlainTextResponse, JSONResponse


class zephyrpy:
    def __init__(
        self,
        cors: bool = False,
        cors_config: Optional[dict] = None,
        csrf: bool = False,
        csrf_config: Optional[dict] = None,
        rate_limit: bool = False,
        rate_limit_config: Optional[dict] = None,
    ):
        self.router = Router()
        self.openapi_info = {
            "title": "zephyrpy API",
            "version": "1.0.0",
            "description": "A minimal, async-first Python web framework with low memory usage and ultra-low latency.",
        }
        self._routes_openapi = []

        # Start with core app
        current_app = self

        if rate_limit:
            rate_limit_config = rate_limit_config or {}
            from .middleware.rate_limit import RateLimitMiddleware

            current_app = RateLimitMiddleware(current_app, **rate_limit_config)

        if csrf:
            csrf_config = csrf_config or {}
            from .middleware.csrf import CSRFMiddleware

            current_app = CSRFMiddleware(current_app, **csrf_config)

        if cors:
            cors_config = cors_config or {}
            from .middleware.cors import CORSMiddleware

            current_app = CORSMiddleware(current_app, **cors_config)

        self._asgi_app = current_app

        # Add OpenAPI routes to CORE (not wrapped)
        self.add_route("/openapi.json", self._serve_openapi, methods=["GET"])
        self.add_route("/docs", self._serve_swagger_ui, methods=["GET"])

    def add_route(self, path: str, handler: Callable, methods=None):
        if methods is None:
            methods = ["GET"]
        self.router.add_route(path, handler, methods)

    def route(self, path: str, methods=None):
        def decorator(handler):
            self.add_route(path, handler, methods)
            return handler

        return decorator

    def openapi(
        self,
        path: str,
        methods=None,
        summary: str = "",
        description: str = "",
        request_body: dict = None,
        responses: dict = None,
    ):
        if methods is None:
            methods = ["GET"]
        if responses is None:
            responses = {200: {"description": "Successful Response"}}

        def decorator(handler):
            self.add_route(path, handler, methods)
            self._routes_openapi.append(
                {
                    "path": path,
                    "methods": [m.upper() for m in methods],
                    "summary": summary,
                    "description": description,
                    "request_body": request_body,
                    "responses": responses,
                }
            )
            return handler

        return decorator

    def generate_openapi(self):
        paths = {}
        for item in self._routes_openapi:
            path = item["path"]
            path_item = paths.setdefault(path, {})
            for method in item["methods"]:
                operation = {
                    "summary": item["summary"],
                    "description": item["description"],
                    "responses": item["responses"],
                }
                if item["request_body"]:
                    operation["requestBody"] = {
                        "content": {
                            "application/json": {"schema": item["request_body"]}
                        }
                    }
                path_item[method.lower()] = operation

        return {
            "openapi": "3.0.3",
            "info": self.openapi_info,
            "paths": paths,
        }

    async def _serve_openapi(self, request):
        return JSONResponse(self.generate_openapi())

    async def _serve_swagger_ui(self, request):
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Swagger UI - zephyrpy</title>
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css" />
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
            <script>
                SwaggerUIBundle({{
                    url: "/openapi.json",
                    dom_id: "#swagger-ui",
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIBundle.SwaggerUIStandalonePreset
                    ],
                    layout: "BaseLayout"
                }});
            </script>
        </body>
        </html>
        """
        return PlainTextResponse(
            html, headers={"content-type": "text/html; charset=utf-8"}
        )

    # Core ASGI app (no middleware)
    async def __call__(self, scope: Dict[str, Any], receive, send):
        if scope["type"] != "http":
            if scope["type"] == "lifespan":
                while True:
                    message = await receive()
                    if message["type"] == "lifespan.startup":
                        await send({"type": "lifespan.startup.complete"})
                    elif message["type"] == "lifespan.shutdown":
                        await send({"type": "lifespan.shutdown.complete"})
                        break
            return

        request = Request(scope, receive)
        response = await self._handle_request(request)
        await response(scope, receive, send)

    async def _handle_request(self, request: "Request"):
        handler, kwargs = self.router.resolve(request.path, request.method)
        if handler is None:
            return PlainTextResponse("Not Found", status_code=404)

        try:
            result = handler(request, **kwargs)
            if asyncio.iscoroutine(result):
                result = await result
        except Exception as e:
            return PlainTextResponse("Internal Server Error", status_code=500)

        if isinstance(result, Response):
            return result
        elif isinstance(result, dict):
            return JSONResponse(result)
        else:
            return PlainTextResponse(str(result))

    def run(self, host="127.0.0.1", port=8000, reload=False):
        raise RuntimeError("Use 'zephyrpy run --app your_module:app' instead.")
