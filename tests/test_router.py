# tests/test_router.py
from zephyr.router import Router

def dummy_handler(request, **kwargs):
    return {"kwargs": kwargs}

def test_router_basic():
    router = Router()
    router.add_route("/hello", dummy_handler, ["GET"])
    handler, kwargs = router.resolve("/hello", "GET")
    assert handler == dummy_handler
    assert kwargs == {}

def test_router_path_params():
    router = Router()
    router.add_route("/user/{user_id:int}", dummy_handler, ["GET"])
    handler, kwargs = router.resolve("/user/123", "GET")
    assert handler == dummy_handler
    assert kwargs == {"user_id": 123}

def test_router_invalid_int():
    router = Router()
    router.add_route("/item/{id:int}", dummy_handler, ["GET"])
    handler, kwargs = router.resolve("/item/abc", "GET")
    assert handler is None

def test_router_str_param():
    router = Router()
    router.add_route("/search/{query:str}", dummy_handler, ["GET"])
    handler, kwargs = router.resolve("/search/hello%20world", "GET")
    assert handler == dummy_handler
    assert kwargs == {"query": "hello%20world"}

def test_router_not_found():
    router = Router()
    router.add_route("/api/data", dummy_handler, ["GET"])
    handler, kwargs = router.resolve("/api/missing", "GET")
    assert handler is None