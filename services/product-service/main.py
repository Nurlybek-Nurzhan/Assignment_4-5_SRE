from fastapi import FastAPI
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import json
import os
import uvicorn

app = FastAPI(title="Product Service")

REQUEST_COUNT = Counter("product_requests_total", "Total requests to product service", ["method", "endpoint"])

DATA_FILE = "/app/data/products.json"

DEFAULT_PRODUCTS = [
    {"id": 1, "name": "Laptop",   "price": 999.99, "stock": 10},
    {"id": 2, "name": "Mouse",    "price": 29.99,  "stock": 50},
    {"id": 3, "name": "Keyboard", "price": 79.99,  "stock": 30},
    {"id": 4, "name": "Monitor",  "price": 399.99, "stock": 15},
]

def load_products():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    save_products(DEFAULT_PRODUCTS)
    return DEFAULT_PRODUCTS

def save_products(products):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(products, f)

@app.get("/health")
def health():
    REQUEST_COUNT.labels(method="GET", endpoint="/health").inc()
    return {"status": "ok", "service": "product-service"}

@app.get("/products")
def get_products():
    REQUEST_COUNT.labels(method="GET", endpoint="/products").inc()
    products = load_products()
    return {"products": products, "total": len(products)}

@app.get("/products/{product_id}")
def get_product(product_id: int):
    REQUEST_COUNT.labels(method="GET", endpoint="/products/{id}").inc()
    for p in load_products():
        if p["id"] == product_id:
            return p
    return {"error": "Product not found"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
