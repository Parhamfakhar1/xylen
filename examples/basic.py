# examples/basic.py
from zephyr import Zephyr
import os

os.environ["ZEPHYR_SECRET_KEY"] = "dev-secret-key-for-zephyr"

app = Zephyr(
    cors=True,
    cors_config={
        "allow_origins": ["*"],
        "allow_methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["content-type", "authorization"],
    },
    rate_limit=True,
    rate_limit_config={"max_requests": 10, "window_seconds": 60},
)


@app.openapi(
    path="/hello",
    methods=["GET"],
    summary="Say Hello",
    description="Returns a friendly greeting.",
    responses={
        200: {
            "description": "A JSON object with message",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {"message": {"type": "string"}},
                    }
                }
            },
        }
    },
)
async def hello(request):
    return {"message": "Hello from Zephyr!"}


@app.openapi(
    path="/user/{user_id:int}",
    methods=["GET"],
    summary="Get User by ID",
    description="Fetch user details using numeric ID.",
    responses={
        200: {
            "description": "User data",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {"user_id": {"type": "integer"}},
                    }
                }
            },
        },
        404: {"description": "User not found"},
    },
)
def user_detail(request, user_id: int):
    return {"user_id": user_id}
