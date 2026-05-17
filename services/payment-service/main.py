from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import os
import time
import uuid
import uvicorn

app = FastAPI(title="Payment Service")

REQUEST_COUNT   = Counter("payment_requests_total",   "Total requests to payment service", ["method", "endpoint"])
ERROR_COUNT     = Counter("payment_errors_total",      "Total errors in payment service",   ["type"])
REQUEST_LATENCY = Histogram(
    "payment_request_duration_seconds",
    "Request latency for payment service endpoints",
    ["endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
)
PAYMENT_SUCCESS = Counter("payment_success_total", "Total successful payments")
PAYMENT_FAILURE = Counter("payment_failure_total", "Total failed payments")

class PaymentRequest(BaseModel):
    order_id: int
    amount: float
    currency: str = "USD"
    card_last4: str = "4242"

@app.get("/health")
def health():
    REQUEST_COUNT.labels(method="GET", endpoint="/health").inc()
    return {"status": "ok", "service": "payment-service"}

@app.post("/pay")
def process_payment(req: PaymentRequest):
    REQUEST_COUNT.labels(method="POST", endpoint="/pay").inc()
    start = time.time()
    try:
        if req.amount <= 0:
            ERROR_COUNT.labels(type="invalid_amount").inc()
            PAYMENT_FAILURE.inc()
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")

        # Simulate occasional payment decline (card ending in 0000)
        if req.card_last4 == "0000":
            ERROR_COUNT.labels(type="card_declined").inc()
            PAYMENT_FAILURE.inc()
            REQUEST_LATENCY.labels(endpoint="/pay").observe(time.time() - start)
            raise HTTPException(status_code=402, detail="Card declined")

        time.sleep(0.01)  # simulate processing delay
        transaction_id = str(uuid.uuid4())
        PAYMENT_SUCCESS.inc()
        REQUEST_LATENCY.labels(endpoint="/pay").observe(time.time() - start)
        return {
            "transaction_id": transaction_id,
            "order_id": req.order_id,
            "amount": req.amount,
            "currency": req.currency,
            "status": "approved",
        }
    except HTTPException:
        raise
    except Exception as e:
        ERROR_COUNT.labels(type="internal").inc()
        PAYMENT_FAILURE.inc()
        REQUEST_LATENCY.labels(endpoint="/pay").observe(time.time() - start)
        raise HTTPException(status_code=500, detail=f"Payment processing error: {str(e)}")

@app.get("/payments/{order_id}")
def get_payment_status(order_id: int):
    REQUEST_COUNT.labels(method="GET", endpoint="/payments").inc()
    return {"order_id": order_id, "status": "approved", "note": "mock response"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8006)
