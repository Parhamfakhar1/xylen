# tests/test_responses.py
from zephyr.response import PlainTextResponse, JSONResponse

def test_plain_text_response():
    resp = PlainTextResponse("Hello", status_code=201)
    assert resp.status_code == 201
    assert resp.body == b"Hello"

def test_json_response():
    data = {"message": "OK", "code": 200}
    resp = JSONResponse(data)
    assert resp.status_code == 200
    assert b'"message": "OK"' in resp.body
    assert resp.headers[b"content-type"] == b"application/json; charset=utf-8"