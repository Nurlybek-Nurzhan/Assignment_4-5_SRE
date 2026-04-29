from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import psycopg2
import os
import time
import uvicorn

app = FastAPI(title="Order Service")

REQUEST_COUNT   = Counter("order_requests_total",   "Total requests to order service", ["method", "endpoint"])
ERROR_COUNT     = Counter("order_errors_total",      "Total errors in order service",   ["type"])
REQUEST_LATENCY = Histogram(
    "order_request_duration_seconds",
    "Request latency for order service endpoints",
    ["endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
)

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ordersdb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS")
if not DB_PASS:
    raise RuntimeError("DB_PASS environment variable is required but not set")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        dbname=DB_NAME, user=DB_USER, password=DB_PASS,
        connect_timeout=3
    )

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id INT NOT NULL,
                product_id INT NOT NULL,
                quantity INT NOT NULL,
                status VARCHAR(50) DEFAULT 'pending'
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB init error: {e}")

class OrderRequest(BaseModel):
    user_id: int
    product_id: int
    quantity: int

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    REQUEST_COUNT.labels(method="GET", endpoint="/health").inc()
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "ok", "service": "order-service", "db": "connected"}
    except Exception as e:
        ERROR_COUNT.labels(type="db_connection").inc()
        raise HTTPException(status_code=503, detail=f"DB connection failed: {str(e)}")

@app.get("/orders")
def get_orders():
    REQUEST_COUNT.labels(method="GET", endpoint="/orders").inc()
    start = time.time()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, user_id, product_id, quantity, status FROM orders")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        REQUEST_LATENCY.labels(endpoint="/orders").observe(time.time() - start)
        return {"orders": [{"id": r[0], "user_id": r[1], "product_id": r[2], "quantity": r[3], "status": r[4]} for r in rows]}
    except Exception as e:
        ERROR_COUNT.labels(type="db_query").inc()
        REQUEST_LATENCY.labels(endpoint="/orders").observe(time.time() - start)
        raise HTTPException(status_code=503, detail=f"DB error: {str(e)}")

@app.post("/orders")
def create_order(order: OrderRequest):
    REQUEST_COUNT.labels(method="POST", endpoint="/orders").inc()
    start = time.time()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO orders (user_id, product_id, quantity) VALUES (%s, %s, %s) RETURNING id",
            (order.user_id, order.product_id, order.quantity)
        )
        order_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        REQUEST_LATENCY.labels(endpoint="/orders").observe(time.time() - start)
        return {"order_id": order_id, "status": "pending"}
    except Exception as e:
        ERROR_COUNT.labels(type="db_insert").inc()
        REQUEST_LATENCY.labels(endpoint="/orders").observe(time.time() - start)
        raise HTTPException(status_code=503, detail=f"DB error: {str(e)}")

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
