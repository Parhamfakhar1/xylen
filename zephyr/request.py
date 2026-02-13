# zephyr/request.py
class Request:
    def __init__(self, scope, receive):
        self.scope = scope
        self.method = scope["method"]
        self.path = scope["path"]
        self.headers = dict(scope["headers"])