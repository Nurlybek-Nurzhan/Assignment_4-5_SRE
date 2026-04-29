# MicroShop - SRE Assignment 4-5

Containerized microservices system with incident response simulation and Terraform IaC on AWS.

**GitHub:** https://github.com/Nurlybek-Nurzhan/Assignment_4-5_SRE

---

## Services

| Service        | Port | Description                        |
|----------------|------|------------------------------------|
| Frontend       | 80   | Dashboard (Nginx reverse proxy)    |
| Auth Service   | 8001 | Login / JWT authentication         |
| Product Service| 8002 | Product catalog (file-persisted)   |
| Order Service  | 8003 | Order management (PostgreSQL)      |
| User Service   | 8004 | User profiles                      |
| Chat Service   | 8005 | Messaging (JWT-protected)          |
| Prometheus     | 9090 | Metrics collection + alert rules   |
| Grafana        | 3000 | Auto-provisioned dashboards        |

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
- Grafana: http://localhost:3000 (credentials from .env)

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
#   DB_HOST: postgres
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
#   DB_HOST: postgres

docker compose up -d --force-recreate order-service

# Verify recovery:
curl http://localhost:8003/health
# Returns: {"status": "ok", "db": "connected"}
```

---

## Terraform (Assignment 5)

Provisions an AWS EC2 instance (t3.micro) with a security group opening ports 22, 80, 3000, 9090.

```bash
cd terraform

# Configure AWS credentials first
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
│   ├── prometheus.yml      # Scrape config
│   ├── alert_rules.yml     # OrderServiceErrors + ServiceDown alerts
│   └── grafana/
│       └── provisioning/   # Auto-provisioned datasource + dashboard
├── terraform/
│   ├── main.tf             # AWS EC2 + security group
│   ├── variables.tf
│   ├── outputs.tf
│   └── terraform.tfvars
├── docker-compose.yml
├── .env.example
└── README.md
```
