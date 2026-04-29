from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import uvicorn

app = FastAPI(title="Auth Service")

REQUEST_COUNT = Counter("auth_requests_total", "Total requests to auth service", ["method", "endpoint"])

USERS = {"nurzhan": "password123", "admin": "admin"}

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
    if USERS.get(req.username) == req.password:
        return {"token": "fake-jwt-token-123", "username": req.username}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
