# request.py
class Request:
    def __init__(self, scope, receive):
        self.scope = scope
        self.method = scope["method"]
        self.path = scope["path"]
        self.headers = {k.decode(): v.decode() for k, v in scope["headers"]}
        self._receive = receive
        self._body = None

    async def body(self):
        if self._body is not None:
            return self._body
        body = b""
        more_body = True
        while more_body:
            message = await self._receive()
            if message["type"] == "http.request":
                body += message.get("body", b"")
                more_body = message.get("more_body", False)
        self._body = body
        return body

    async def json(self):
        import json
        return json.loads(await self.body())