#!/usr/bin/env python3
import argparse
import threading
import time
import urllib.request
import urllib.error
import json
import sys
from collections import defaultdict

parser = argparse.ArgumentParser(description="MicroShop load simulator")
parser.add_argument(
    "--host", default="http://localhost", help="Base URL of the frontend/Nginx"
)
parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds")
parser.add_argument(
    "--workers", type=int, default=10, help="Number of concurrent worker threads"
)
args = parser.parse_args()

BASE = args.host.rstrip("/")
DURATION = args.duration
WORKERS = args.workers

lock = threading.Lock()
counts = defaultdict(int)
errors = defaultdict(int)
stop_evt = threading.Event()


def request(path, method="GET", data=None, token=None):
    url = f"{BASE}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception:
        return 0, {}


def get_token():
    status, body = request(
        "/api/auth/login", "POST", {"username": "nurzhan", "password": "password123"}
    )
    if status == 200:
        return body.get("token")
    return None


def worker():
    token = get_token()
    while not stop_evt.is_set():
        for path in [
            "/api/products/products",
            "/api/orders/orders",
            "/api/auth/health",
            "/api/products/health",
            "/api/orders/health",
        ]:
            if stop_evt.is_set():
                break
            status, _ = request(path)
            with lock:
                counts[path] += 1
                if status not in (200, 201):
                    errors[path] += 1

        if token:
            for path in ["/api/users/users", "/api/chat/messages"]:
                if stop_evt.is_set():
                    break
                status, _ = request(path, token=token)
                with lock:
                    counts[path] += 1
                    if status not in (200, 201):
                        errors[path] += 1

        if stop_evt.is_set():
            break
        status, _ = request(
            "/api/orders/orders", "POST", {"user_id": 1, "product_id": 1, "quantity": 1}
        )
        with lock:
            counts["POST /api/orders/orders"] += 1
            if status not in (200, 201):
                errors["POST /api/orders/orders"] += 1

        time.sleep(0.05)


print(f"Starting load test: {WORKERS} workers × {DURATION}s against {BASE}")
print("Watch Grafana at http://localhost:3000 — refresh every 10s\n")

threads = [threading.Thread(target=worker, daemon=True) for _ in range(WORKERS)]
for t in threads:
    t.start()

start = time.time()
try:
    while time.time() - start < DURATION:
        elapsed = int(time.time() - start)
        with lock:
            total = sum(counts.values())
            errs = sum(errors.values())
        rps = total / max(elapsed, 1)
        print(
            f"\r[{elapsed:>3}s] total={total:>6}  errors={errs:>4}  RPS={rps:>6.1f}",
            end="",
            flush=True,
        )
        time.sleep(1)
except KeyboardInterrupt:
    print("\nInterrupted by user.")

stop_evt.set()
for t in threads:
    t.join(timeout=3)

elapsed = time.time() - start
total = sum(counts.values())
errs = sum(errors.values())
print(f"\n\n{'─'*55}")
print(f"Duration : {elapsed:.1f}s")
print(f"Workers  : {WORKERS}")
print(f"Total req: {total}")
print(f"Errors   : {errs}  ({100*errs/max(total,1):.1f}%)")
print(f"Avg RPS  : {total/elapsed:.1f}")
print(f"{'─'*55}")
print(f"{'Endpoint':<40} {'Reqs':>6} {'Errs':>6}")
print(f"{'─'*55}")
for path in sorted(counts):
    print(f"{path:<40} {counts[path]:>6} {errors[path]:>6}")
print(f"{'─'*55}")
print("\nDone. Check Grafana for CPU, latency and error rate panels.")
