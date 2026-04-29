# MicroShop — SRE Assignment 4-5

Microservices system with incident response simulation and Terraform IaC.

## Services

| Service | Port | Description |
|---|---|---|
| Frontend | 80 | Dashboard (Nginx) |
| Auth Service | 8001 | Login / authentication |
| Product Service | 8002 | Product catalog |
| Order Service | 8003 | Order management (PostgreSQL) |
| User Service | 8004 | User profiles |
| Chat Service | 8005 | User messaging |
| Prometheus | 9090 | Metrics collection |
| Grafana | 3000 | Dashboards (admin/admin) |

## Quick Start

```bash
cd assignment-4-5
docker compose up --build
```

Open http://localhost:80 to see the dashboard.

## Incident Simulation (Assignment 4)

Break the Order Service:
```bash
# Edit docker-compose.yml — change DB_HOST to wrong-host
docker compose up -d --force-recreate order-service
```

Fix it:
```bash
# Restore DB_HOST: postgres
docker compose up -d --force-recreate order-service
```

## Terraform (Assignment 5)

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

Tears down with:
```bash
terraform destroy
```
