from fastapi import FastAPI
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import uvicorn

app = FastAPI(title="User Service")

REQUEST_COUNT = Counter("user_requests_total", "Total requests to user service", ["method", "endpoint"])

USERS = [
    {"id": 1, "username": "nurzhan", "email": "nurzhan@example.com", "role": "admin"},
    {"id": 2, "username": "alice", "email": "alice@example.com", "role": "user"},
    {"id": 3, "username": "bob", "email": "bob@example.com", "role": "user"},
]

@app.get("/health")
def health():
    REQUEST_COUNT.labels(method="GET", endpoint="/health").inc()
    return {"status": "ok", "service": "user-service"}

@app.get("/users")
def get_users():
    REQUEST_COUNT.labels(method="GET", endpoint="/users").inc()
    return {"users": USERS, "total": len(USERS)}

@app.get("/users/{user_id}")
def get_user(user_id: int):
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
