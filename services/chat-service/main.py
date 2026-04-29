from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from jose import jwt, JWTError
from datetime import datetime
import os
import uvicorn

app = FastAPI(title="Chat Service")

REQUEST_COUNT = Counter("chat_requests_total", "Total requests to chat service", ["method", "endpoint"])

SECRET_KEY = os.environ.get("JWT_SECRET")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET environment variable is required but not set")
ALGORITHM = "HS256"

MESSAGES = [
    {"id": 1, "from_user": "alice", "to_user": "bob",   "text": "Hey Bob!",   "timestamp": "2026-04-29T10:00:00"},
    {"id": 2, "from_user": "bob",   "to_user": "alice", "text": "Hi Alice!", "timestamp": "2026-04-29T10:01:00"},
]

def verify_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

class MessageRequest(BaseModel):
    from_user: str
    to_user: str
    text: str

@app.get("/health")
def health():
    REQUEST_COUNT.labels(method="GET", endpoint="/health").inc()
    return {"status": "ok", "service": "chat-service"}

@app.get("/messages")
def get_messages(authorization: str | None = Header(default=None)):
    verify_token(authorization)
    REQUEST_COUNT.labels(method="GET", endpoint="/messages").inc()
    return {"messages": MESSAGES, "total": len(MESSAGES)}

@app.post("/messages")
def send_message(msg: MessageRequest, authorization: str | None = Header(default=None)):
    verify_token(authorization)
    REQUEST_COUNT.labels(method="POST", endpoint="/messages").inc()
    new_msg = {
        "id": len(MESSAGES) + 1,
        "from_user": msg.from_user,
        "to_user": msg.to_user,
        "text": msg.text,
        "timestamp": datetime.now().isoformat()
    }
    MESSAGES.append(new_msg)
    return new_msg

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
