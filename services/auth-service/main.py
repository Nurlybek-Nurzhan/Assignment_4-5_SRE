from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from jose import jwt
from passlib.context import CryptContext
import os
import uvicorn

app = FastAPI(title="Auth Service")

REQUEST_COUNT = Counter("auth_requests_total", "Total requests to auth service", ["method", "endpoint"])

SECRET_KEY = os.getenv("JWT_SECRET", "changeme-super-secret-key")
ALGORITHM  = "HS256"

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Credentials loaded from environment variables, not hardcoded
_raw = {
    os.getenv("AUTH_USER_1", "nurzhan"): os.getenv("AUTH_PASS_1", "password123"),
    os.getenv("AUTH_USER_2", "admin"):   os.getenv("AUTH_PASS_2", "admin"),
}
USERS = {u: pwd_ctx.hash(p) for u, p in _raw.items()}

class LoginRequest(BaseModel):
    username: str
    password: str

@app.get("/health")
def health():
    REQUEST_COUNT.labels(method="GET", endpoint="/health").inc()
    return {"status": "ok", "service": "auth-service"}

@app.post("/login")
def login(req: LoginRequest):
    REQUEST_COUNT.labels(method="POST", endpoint="/login").inc()
    hashed = USERS.get(req.username)
    if not hashed or not pwd_ctx.verify(req.password, hashed):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = jwt.encode({"sub": req.username}, SECRET_KEY, algorithm=ALGORITHM)
    return {"token": token, "username": req.username}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
