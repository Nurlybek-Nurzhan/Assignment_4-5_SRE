from fastapi import FastAPI, HTTPException, Header
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from jose import jwt, JWTError
import os
import uvicorn

app = FastAPI(title="User Service")

REQUEST_COUNT = Counter("user_requests_total", "Total requests to user service", ["method", "endpoint"])

SECRET_KEY = os.getenv("JWT_SECRET", "changeme-super-secret-key")
ALGORITHM  = "HS256"

USERS = [
    {"id": 1, "username": "nurzhan", "email": "nurzhan@example.com", "role": "admin"},
    {"id": 2, "username": "alice",   "email": "alice@example.com",   "role": "user"},
    {"id": 3, "username": "bob",     "email": "bob@example.com",     "role": "user"},
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

@app.get("/health")
def health():
    REQUEST_COUNT.labels(method="GET", endpoint="/health").inc()
    return {"status": "ok", "service": "user-service"}

@app.get("/users")
def get_users(authorization: str | None = Header(default=None)):
    verify_token(authorization)
    REQUEST_COUNT.labels(method="GET", endpoint="/users").inc()
    return {"users": USERS, "total": len(USERS)}

@app.get("/users/{user_id}")
def get_user(user_id: int, authorization: str | None = Header(default=None)):
    verify_token(authorization)
    REQUEST_COUNT.labels(method="GET", endpoint="/users/{id}").inc()
    for u in USERS:
        if u["id"] == user_id:
            return u
    return {"error": "User not found"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)
