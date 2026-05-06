# MicroShop - SRE Assignment 4-5-6

Containerized microservices system with incident response simulation, Terraform IaC on AWS, Alertmanager, and centralized log aggregation with Loki/Promtail.

**GitHub:** https://github.com/Nurlybek-Nurzhan/Assignment_4-5_SRE

---

## Services

| Service        | Host Port | Internal Port | Description                              |
|----------------|-----------|---------------|------------------------------------------|
| Frontend       | 80        | 80            | Dashboard (Nginx reverse proxy)          |
| Prometheus     | 9090      | 9090          | Metrics collection + alert rules         |
| Alertmanager   | 9093      | 9093          | Alert routing and notification           |
| Loki           | 3100      | 3100          | Log aggregation backend                  |
| Grafana        | 3000      | 3000          | Dashboards (metrics + logs)              |
| Auth Service   | —         | 8001          | JWT authentication (internal only)       |
| Product Service| —         | 8002          | Product catalog (internal only)          |
| Order Service  | —         | 8003          | Order management (internal only)         |
| User Service   | —         | 8004          | User profiles (internal only)            |
| Chat Service   | —         | 8005          | Messaging (internal only)                |

> **Security note:** Microservices (8001-8005) are NOT bound to the host. They are only reachable through the Nginx reverse proxy on port 80, or from within the Docker network.

---

## Quick Start

```bash
# 1. Copy env file and configure secrets
cp .env.example .env

# 2. Build and start all containers
docker compose up --build
```

- Dashboard: http://localhost:80
- Prometheus: http://localhost:9090
- Alertmanager: http://localhost:9093
- Grafana: http://localhost:3000 (credentials from .env)
- Loki: http://localhost:3100 (used by Promtail and Grafana internally)

---

## Incident Simulation (Assignment 4)

### What happens
The Order Service connects to PostgreSQL via the `DB_HOST` environment variable.
Setting it to a wrong hostname causes every request to fail immediately - the service
process keeps running (so Prometheus shows it as `up=1`), but all business logic fails.

**This is a key SRE lesson:** process liveness ≠ service health.
Prometheus scrapes `/metrics` (which always responds), so `up` stays 1 even during the incident.
The real signal comes from `/health` (which checks DB connectivity) and the `order_errors_total` counter.

### Incident Timeline

| Time    | Event |
|---------|-------|
| T+00:00 | `DB_HOST` changed to `wrong-host` in docker-compose.yml |
| T+00:05 | Order Service restarted: `docker compose up -d --force-recreate order-service` |
| T+00:10 | Frontend dashboard shows Order Service as **Unreachable** |
| T+00:15 | `/api/orders/orders` returns HTTP 503 |
| T+00:20 | `order_errors_total` counter starts incrementing in Prometheus |
| T+00:25 | `/health` returns 503: `DB connection failed: could not translate host name 'wrong-host'` |
| T+00:30 | `docker logs order-service` confirms: repeated psycopg2 DNS errors |
| T+01:00 | Root cause confirmed: wrong `DB_HOST` value |
| T+01:05 | `DB_HOST` corrected back to `postgres` in docker-compose.yml |
| T+01:10 | Order Service restarted with correct config |
| T+01:15 | `/health` returns 200: `db: connected` |
| T+01:20 | Dashboard shows all services green - incident resolved |

### Steps to reproduce

**Break it:**
```bash
# In docker-compose.yml, change:
#   DB_HOST: *correct data*
# to:
#   DB_HOST: wrong-host

docker compose up -d --force-recreate order-service
```

**Observe the failure:**
```bash
# Watch logs - you will see repeated DB connection errors:
docker logs -f order-service

# Check health endpoint:
curl http://localhost:8003/health
# Returns: {"detail": "DB connection failed: could not translate host name 'wrong-host'"}

# Check Prometheus metric:
curl http://localhost:8003/metrics | grep order_errors_total
```

**Fix it:**
```bash
# In docker-compose.yml, restore:
#   DB_HOST *correct data*

docker compose up -d --force-recreate order-service

# Verify recovery:
curl http://localhost:8003/health
# Returns: {"status": "ok", "db": "connected"}
```

---

## Terraform (Assignment 5)

Provisions an AWS EC2 instance (t3.micro) with a security group. Microservice ports (8001-8005) are **not opened** in the security group — only port 80 (HTTP), 3000 (Grafana), 9090 (Prometheus), 9093 (Alertmanager), and 22 (SSH) are exposed, all except HTTP restricted to `allowed_ssh_cidr`.

```bash
cd terraform

# 1. Find your public IP
curl -s ifconfig.me   # e.g. 203.0.113.42

# 2. Set your IP in terraform.tfvars
#    allowed_ssh_cidr = "203.0.113.42/32"

# 3. Configure AWS credentials
aws configure

terraform init
terraform plan
terraform apply
```

Output after apply:
```
instance_public_ip  = "34.238.137.187"
grafana_url         = "http://34.238.137.187:3000"
prometheus_url      = "http://34.238.137.187:9090"
```

Tear down (avoid AWS charges):
```bash
terraform destroy
```

---

## Alertmanager (Assignment 6)

Alert rules fire in Prometheus and are forwarded to Alertmanager at `alertmanager:9093`. Alertmanager routes them by severity:

| Severity | Receiver         | Repeat interval |
|----------|-----------------|-----------------|
| critical | critical-receiver | 15 minutes    |
| warning  | default-receiver  | 1 hour        |

The webhook receiver at `localhost:5001` is a placeholder — replace with a real Slack/email/PagerDuty endpoint in `monitoring/alertmanager.yml`.

---

## Log Aggregation with Loki + Promtail (Assignment 6)

Promtail runs as a sidecar and collects all Docker container logs via the Docker socket, tagging each log stream with `container`, `service`, and `compose_project` labels. Logs are pushed to Loki and are queryable in Grafana using the Loki datasource.

**To explore logs in Grafana:**
1. Open Grafana → Explore
2. Select datasource: **Loki**
3. Query: `{service="order-service"}` to see order service logs
4. During incident: `{service="order-service"} |= "error"` to filter errors

---

## Security: Port Hardening

**Docker (не забудь закрыть порты — don't forget to close ports):**
- Microservices (8001-8005): **no host binding** — internal Docker network only
- Nginx on port 80: the single public entry point
- Prometheus 9090 and Grafana 3000: host-bound for dev/monitoring access only

**AWS Security Group:**
- Port 22 (SSH): restricted to `allowed_ssh_cidr` (your IP/32)
- Port 80 (HTTP): public
- Port 3000, 9090, 9093: restricted to `allowed_ssh_cidr`
- Ports 8001-8005: **not opened at all** — microservices never exposed through the firewall

---

## Capacity Planning (Assignment 6)

### Load Simulation

Use the included script to generate concurrent load against all services:

```bash
# Default: 10 workers, 60 seconds
python load_test.py

# Higher load for stress testing
python load_test.py --workers 20 --duration 120

# Against AWS EC2
python load_test.py --host http://<instance_public_ip> --workers 10 --duration 60
```

The script sends requests to all endpoints (products, orders, users, chat) via the Nginx reverse proxy and prints a live RPS + error counter. Watch Grafana at http://localhost:3000 during the run.

### Metrics Collected

| Metric | Prometheus expression | Where visible |
|---|---|---|
| Request rate | `rate(order_requests_total[1m])` | Grafana dashboard |
| Error rate | `rate(order_errors_total[1m])` | Grafana dashboard |
| p95 latency | `histogram_quantile(0.95, rate(order_request_duration_seconds_bucket[5m]))` | Grafana dashboard |
| CPU usage | `rate(process_cpu_seconds_total[1m]) * 100` | Prometheus / alert |
| Memory | `process_resident_memory_bytes` | Prometheus Explore |

### Alert Rules

| Alert | Condition | Severity | For |
|---|---|---|---|
| `ServiceDown` | `up == 0` | critical | 30s |
| `OrderServiceErrors` | `increase(order_errors_total[1m]) > 0` | critical | 30s |
| `OrderServiceHighLatency` | p95 latency > 1s | warning | 1m |
| `HighCPUUsage` | CPU > 80% for any service | warning | 1m |

### Observations Under Load

- **Order Service** is the bottleneck: every request opens a new PostgreSQL connection (no connection pooling), so CPU and latency rise sharply under concurrent load.
- **Database** becomes saturated first — connection queue fills up, causing `db_query` errors to increment.
- Other services (auth, product, user, chat) remain stable under load because they have no DB dependency on hot paths.

### Scaling Strategies

**Horizontal scaling** — run multiple Order Service replicas behind Nginx:
```yaml
# In docker-compose.yml, replace container_name with deploy.replicas (Swarm/K8s)
deploy:
  replicas: 3
```

**Vertical scaling** — increase container resource limits in `docker-compose.yml` or upgrade EC2 instance type in `terraform/terraform.tfvars`.

**Database optimization** — add connection pooling (PgBouncer) in front of PostgreSQL to eliminate per-request connection overhead.

**Long-term** — migrate to Kubernetes with HPA (Horizontal Pod Autoscaler) triggered on CPU threshold via the same `process_cpu_seconds_total` metric already collected by Prometheus.

---

## Project Structure

```
assignment-4-5/
├── services/
│   ├── auth-service/       # FastAPI, JWT auth, bcrypt passwords
│   ├── product-service/    # FastAPI, file-persisted catalog
│   ├── order-service/      # FastAPI, PostgreSQL, incident target
│   ├── user-service/       # FastAPI, user profiles
│   └── chat-service/       # FastAPI, JWT-protected messaging
├── frontend/
│   ├── index.html          # Dashboard with login form
│   └── nginx.conf          # Reverse proxy config
├── monitoring/
│   ├── prometheus.yml      # Scrape config + Alertmanager wiring
│   ├── alert_rules.yml     # OrderServiceErrors, ServiceDown, HighLatency, HighCPU
│   ├── alertmanager.yml    # Alert routing by severity
│   ├── loki.yml            # Loki log storage config
│   ├── promtail.yml        # Docker log collector config
│   └── grafana/
│       └── provisioning/
│           ├── datasources/ # Prometheus + Loki datasources
│           └── dashboards/  # Auto-provisioned dashboard
├── terraform/
│   ├── main.tf             # AWS EC2 + security group (ports hardened)
│   ├── variables.tf
│   ├── outputs.tf
│   └── terraform.tfvars    # Set allowed_ssh_cidr to YOUR_IP/32
├── load_test.py            # Concurrent load simulator (Assignment 6)
├── docker-compose.yml
├── .env.example
└── README.md
```
