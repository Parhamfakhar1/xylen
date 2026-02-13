# zephyr/middleware/rate_limit.py
import time
from collections import defaultdict, deque
from ..response import PlainTextResponse

class RateLimitMiddleware:
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        self.app = app
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # {ip: deque([timestamps])}
        self._requests = defaultdict(deque)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        client_ip = self._get_client_ip(scope)
        now = time.time()

        bucket = self._requests[client_ip]
        while bucket and bucket[0] < now - self.window_seconds:
            bucket.popleft()

        if len(bucket) >= self.max_requests:
            response = PlainTextResponse(
                "Too Many Requests", status_code=429,
                headers={"Retry-After": str(self.window_seconds)}
            )
            await response({}, None, send)
            return

        bucket.append(now)

        await self.app(scope, receive, send)

    def _get_client_ip(self, scope):
        client = scope.get("client")
        if client:
            return client[0]  # IP
        return "unknown"