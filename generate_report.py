from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

SCREENSHOTS = os.path.join(os.path.dirname(__file__), "screenshots")
OUTPUT = os.path.join(os.path.dirname(__file__), "Assignment_4_5_Report.docx")

doc = Document()

for section in doc.sections:
    section.top_margin    = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin   = Cm(3)
    section.right_margin  = Cm(2)

def font(run, size=11, bold=False, color=None):
    run.font.name = "Calibri"
    run.font.size = Pt(size)
    run.font.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)

def h1(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after  = Pt(6)
    r = p.add_run(text)
    font(r, 16, True, (31, 73, 125))

def h2(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after  = Pt(4)
    r = p.add_run(text)
    font(r, 13, True, (31, 73, 125))

def h3(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after  = Pt(2)
    r = p.add_run(text)
    font(r, 11, True)

def body(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(5)
    r = p.add_run(text)
    font(r, 11)

def note(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.left_indent = Cm(0.7)
    r = p.add_run(f"Note: {text}")
    font(r, 10, False, (80, 80, 80))

def bullet(text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(text)
    font(r, 11)

def fig(filename, caption, width=15):
    path = os.path.join(SCREENSHOTS, filename)
    if os.path.exists(path):
        doc.add_picture(path, width=Cm(width))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp = doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp.paragraph_format.space_after = Pt(12)
        r = cp.add_run(f"Figure: {caption}")
        font(r, 9, False, (120, 120, 120))
    else:
        p = doc.add_paragraph()
        r = p.add_run(f"[Missing: {filename}]")
        font(r, 10, False, (200, 0, 0))

def pb():
    doc.add_page_break()

# ═══════════════════════════════════════════════
# TITLE PAGE
# ═══════════════════════════════════════════════
for _ in range(4):
    doc.add_paragraph()

tp = doc.add_paragraph()
tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = tp.add_run("ASSIGNMENT 4–5 REPORT")
font(r, 24, True, (31, 73, 125))

doc.add_paragraph()
tp2 = doc.add_paragraph()
tp2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = tp2.add_run("Incident Response Simulation and\nInfrastructure as Code Implementation")
font(r2, 14)

doc.add_paragraph()
tp3 = doc.add_paragraph()
tp3.alignment = WD_ALIGN_PARAGRAPH.CENTER
r3 = tp3.add_run("MicroShop — Containerized Microservices System")
font(r3, 12, True)

doc.add_paragraph()
tp4 = doc.add_paragraph()
tp4.alignment = WD_ALIGN_PARAGRAPH.CENTER
r4 = tp4.add_run("Introduction to SRE  |  2026")
font(r4, 11, False, (100, 100, 100))

doc.add_paragraph()
tp5 = doc.add_paragraph()
tp5.alignment = WD_ALIGN_PARAGRAPH.CENTER
r5 = tp5.add_run("GitHub: https://github.com/Nurlybek-Nurzhan/Assignment_4-5_SRE")
font(r5, 10, False, (31, 73, 125))

pb()

# ═══════════════════════════════════════════════
# SYSTEM OVERVIEW
# ═══════════════════════════════════════════════
h1("System Overview")
body(
    "MicroShop is a containerized e-commerce platform built to demonstrate SRE practices. "
    "It consists of five independent FastAPI microservices, a PostgreSQL database, an Nginx "
    "frontend acting as a reverse proxy, Prometheus for metrics collection with three alert rules, "
    "and Grafana with an auto-provisioned dashboard. All components run in Docker containers "
    "orchestrated by Docker Compose on a shared internal bridge network (microshop-net)."
)

h2("Architecture")
bullet("Auth Service (port 8001) — JWT authentication with bcrypt password hashing; crashes on startup if JWT_SECRET not set")
bullet("Product Service (port 8002) — product catalog, persisted to a Docker volume via JSON file")
bullet("Order Service (port 8003) — order management, PostgreSQL backend, Histogram latency metrics; crashes if DB_PASS or JWT_SECRET not set")
bullet("User Service (port 8004) — user profile management with JWT token verification; crashes if JWT_SECRET not set")
bullet("Chat Service (port 8005) — messaging with JWT token verification; crashes if JWT_SECRET not set")
bullet("PostgreSQL — persistent database used exclusively by the Order Service")
bullet("Prometheus (port 9090) — scrapes /metrics from all five services; three alert rules defined")
bullet("Grafana (port 3000) — auto-provisioned datasource and dashboard on startup")
bullet("Nginx (port 80) — serves the frontend, proxies /api/* routes to backend services")

h2("Observability and Metrics")
body(
    "All five services expose Prometheus Counter metrics for request counts. "
    "The Order Service additionally exposes a Histogram metric — "
    "order_request_duration_seconds — with nine latency buckets (5ms to 2.5s). "
    "This enables p50, p95, and p99 latency queries in Grafana, which are the primary "
    "signals used in production SLO monitoring."
)
body(
    "Three Prometheus alert rules are defined in monitoring/alert_rules.yml:"
)
bullet("OrderServiceErrors — fires when order_errors_total increases (DB connection broken)")
bullet("ServiceDown — fires when any scrape target returns up=0 (process crashed)")
bullet("OrderServiceHighLatency — fires when p95 latency exceeds 1 second for 1 minute")

h2("Security Hardening")
bullet("All credentials stored in .env file, never hardcoded in source")
bullet("Passwords hashed with bcrypt — plaintext never stored")
bullet("Real JWT tokens (HS256) issued on login; Chat, User services validate on every request")
bullet("Services crash at startup with RuntimeError if JWT_SECRET or DB_PASS env vars are missing")
bullet("All containers have enforced memory and CPU limits (mem_limit / cpus top-level keys)")
bullet("Docker healthchecks on all services — Docker knows if app is ready, not just started")
bullet("terraform.tfstate excluded from git — contains sensitive AWS resource IDs")
bullet("allowed_ssh_cidr has no default in variables.tf — terraform apply fails if not explicitly set")

h2("Known Limitations (Assignment Scope)")
bullet("Auth service uses two hardcoded users defined in .env — no user registration flow")
bullet("Chat messages are in-memory only — reset on container restart (no chat DB)")
bullet("User list is a static in-memory list — no persistence across restarts")
bullet("Order Service opens a new psycopg2 connection per request — no connection pooling")
bullet("allowed_ssh_cidr is set to 0.0.0.0/0 in terraform.tfvars for demo purposes — must be restricted to a specific IP in production")

h2("Running System")
fig("1_terminal .png", "docker compose up — all 9 containers started successfully")
fig("2_docker_ps.png", "docker ps — all containers running with correct port mappings")

h2("Frontend Dashboard")
body(
    "The MicroShop Dashboard shows real-time health of all five services with green/red status dots. "
    "The header includes a login form — entering credentials calls the Auth Service and receives "
    "a real JWT token which is then used for authenticated Chat and User Service calls."
)
fig("3_frontend_dashboard.png", "MicroShop Dashboard — all 5 services healthy, login form in header")

h2("Monitoring")
body(
    "Prometheus scrapes all five services every 15 seconds. "
    "Grafana loads the Prometheus datasource and MicroShop dashboard automatically on startup "
    "via provisioning files — no manual configuration needed. "
    "The dashboard includes panels for service health, per-service request rates, "
    "order error rate, total error count, and order latency percentiles."
)
fig("4_prometheus_targets.png", "Prometheus — all 5 service targets showing UP")
fig("5_grafana.png", "Grafana — auto-provisioned dashboard with health, request rate, and error panels")

pb()

# ═══════════════════════════════════════════════
# ASSIGNMENT 4 — INCIDENT REPORT
# ═══════════════════════════════════════════════
h1("ASSIGNMENT 4 — Incident Report")

h2("1. Incident Summary")
body(
    "On 2026-04-29, a production-level incident was simulated in the MicroShop Order Service "
    "by deliberately misconfiguring the DB_HOST environment variable from 'postgres' to 'wrong-host'. "
    "After restarting the container with this broken configuration, the Order Service lost all "
    "database connectivity and returned HTTP 503 on every request. All four other services "
    "remained fully operational throughout the incident, demonstrating correct fault isolation."
)

h2("2. Impact Assessment")
bullet("Order Service: 100% unavailable — /orders (GET and POST) and /health all returned HTTP 503")
bullet("Frontend dashboard: Order Service card showed 'Unreachable' with red status dot")
bullet("Users could not view existing orders or create new ones")
bullet("Auth, Product, User, and Chat services: fully operational — fault isolation confirmed")
bullet("Data integrity: no data lost — PostgreSQL remained healthy throughout")
bullet("Prometheus showed order-service as up=1 — the process was running but functionally broken")

h2("3. Severity Classification")
body("Severity: SEV-2 (Major) — a critical business function (order processing) was completely unavailable.")
body(
    "Classified SEV-2 rather than SEV-1 because the failure was isolated to one service. "
    "Authentication, product browsing, and other features remained functional."
)

h2("4. Timeline of Events")
tbl = doc.add_table(rows=1, cols=2)
tbl.style = "Table Grid"
hdr = tbl.rows[0].cells
hdr[0].text = "Time"
hdr[1].text = "Event"
for cell in hdr:
    for p in cell.paragraphs:
        for r in p.runs:
            font(r, 10, True)

events = [
    ("T+00:00", "DB_HOST changed from 'postgres' to 'wrong-host' in docker-compose.yml"),
    ("T+00:05", "Order Service restarted: docker compose up -d --force-recreate order-service"),
    ("T+00:10", "Frontend dashboard detected Order Service as 'Unreachable'"),
    ("T+00:15", "/api/orders/orders returned HTTP 503 Service Unavailable"),
    ("T+00:20", "order_errors_total counter began incrementing in Prometheus"),
    ("T+00:25", "/health returned 503: 'DB connection failed: could not translate host name wrong-host'"),
    ("T+00:30", "docker logs confirmed repeated psycopg2 DNS resolution failures"),
    ("T+01:00", "Root cause confirmed: incorrect DB_HOST environment variable"),
    ("T+01:05", "DB_HOST corrected back to 'postgres' in docker-compose.yml"),
    ("T+01:10", "Order Service restarted with corrected configuration"),
    ("T+01:15", "/health returned HTTP 200: {status: ok, db: connected}"),
    ("T+01:20", "Frontend dashboard confirmed all services green — full recovery"),
]
for t, e in events:
    row = tbl.add_row().cells
    row[0].text = t
    row[1].text = e
    for cell in row:
        for p in cell.paragraphs:
            for r in p.runs:
                font(r, 10)

doc.add_paragraph()

h2("5. Root Cause Analysis")
body(
    "Root cause: misconfigured DB_HOST environment variable. "
    "Docker Compose services resolve each other by container name through Docker's internal DNS. "
    "The hostname 'postgres' resolves correctly on the microshop-net network. "
    "The value 'wrong-host' has no DNS record, so every call to psycopg2.connect() immediately "
    "raised an OperationalError at the DNS resolution step before attempting any TCP connection."
)
body(
    "Key SRE observation: Prometheus showed order-service as up=1 throughout the incident. "
    "Prometheus scrapes /metrics, which does not touch the database and always responds. "
    "The service process was alive but functionally broken. "
    "This is the critical SRE distinction: process liveness does not equal service health. "
    "The /health endpoint correctly returned 503 with the exact error message. "
    "The order_request_duration_seconds Histogram also showed latency spikes before failures, "
    "which would have triggered the OrderServiceHighLatency alert in a real environment."
)

h2("Incident Evidence")
fig("6_incident_dashboard.png",
    "Dashboard during incident — Order Service 'Unreachable', 503 errors in Network tab")
fig("7_incident_prometheus.png",
    "Prometheus during incident — up=1 for all services. Process alive but DB broken. "
    "Real signal: order_errors_total incrementing.")
fig("8a_incident_logs.png",
    "Docker logs — GET /orders returns 503, GET /metrics returns 200. "
    "Confirms service running but every DB request fails.")
fig("8b_incident_metrics_and_health.png",
    "/health returning 503 with exact error: 'could not translate host name wrong-host' — root cause evidence.")

h2("6. Mitigation Steps")
bullet("Step 1 — docker logs order-service showed repeated 503 on /orders")
bullet("Step 2 — /health endpoint returned exact error with the bad hostname 'wrong-host'")
bullet("Step 3 — Inspected docker-compose.yml: DB_HOST was set to 'wrong-host'")
bullet("Step 4 — Changed DB_HOST back to 'postgres'")
bullet("Step 5 — Restarted only the affected container: docker compose up -d --force-recreate order-service")
bullet("Step 6 — Verified: /health returned 200 with db: connected")
bullet("Step 7 — Confirmed via dashboard: all services green")

h2("7. Resolution Confirmation")
body(
    "Full recovery achieved within approximately 70 seconds of applying the fix. "
    "/health returned HTTP 200, the dashboard showed all five services green, "
    "and the order_errors_total counter stopped incrementing. No data was lost."
)
fig("9_recovery_dashboard.png", "Recovery — all services green, Order Service showing DB: connected")
fig("10a_recovery_logs.png",    "Recovery logs — HTTP 200 responses confirmed after fix")
fig("10b_recovery_metrics_and_health.png", "/health returning 200 with db: connected")

pb()

# ═══════════════════════════════════════════════
# POSTMORTEM
# ═══════════════════════════════════════════════
h1("Postmortem Analysis")

h2("1. Incident Overview")
body(
    "On 2026-04-29, the MicroShop Order Service became fully unavailable for approximately 70 seconds "
    "due to an incorrect database hostname in the service environment configuration. The incident was "
    "intentionally introduced as part of Assignment 4 to simulate a realistic production failure and "
    "practice the complete incident response lifecycle."
)

h2("2. Customer Impact")
bullet("100% of order-related requests failed with HTTP 503 during the incident window")
bullet("Order viewing and creation were completely unavailable")
bullet("Product browsing, authentication, user profiles, and chat were fully unaffected")
bullet("No data loss — PostgreSQL remained healthy and all existing orders were preserved")

h2("3. Root Cause Analysis")
body(
    "The DB_HOST environment variable was manually changed to a non-existent hostname. "
    "Docker Compose services discover each other via Docker's internal DNS using container names. "
    "Setting DB_HOST='wrong-host' caused immediate DNS failure on every database operation. "
    "The service had no retry logic — each request attempted a fresh connection, failed instantly, "
    "incremented order_errors_total, and returned HTTP 503."
)

h2("4. Detection and Response Evaluation")
body(
    "Detection was fast — the frontend dashboard showed the failure within 10 seconds. "
    "The /health endpoint was the critical diagnostic tool: it returned the exact bad hostname "
    "in the error message, making root cause identification immediate."
)
body(
    "Gap identified during incident: Prometheus showed up=1 throughout because it only checks "
    "process liveness via /metrics. The OrderServiceErrors alert rule fires on error counter "
    "increases, and the new OrderServiceHighLatency alert fires on p95 latency exceeding 1 second — "
    "both would catch functional failures that process liveness misses."
)

h2("5. Resolution Summary")
body(
    "A single configuration change (correcting DB_HOST to 'postgres') followed by a container "
    "restart fully restored the service in under 2 minutes. No code changes, no data recovery, "
    "no other service required intervention."
)

h2("6. Lessons Learned")
bullet("Environment variables are a frequent source of misconfiguration in containerized systems")
bullet("Process liveness (up=1) does not mean a service is functionally healthy — dependency checks in /health are essential")
bullet("Histogram metrics (p95/p99 latency) provide earlier warning signals than counters alone")
bullet("Microservices fault isolation worked correctly — one broken service did not cascade to others")
bullet("Services now crash at startup if critical env vars are missing — fail fast beats silent wrong behavior")

h2("7. Action Items")
bullet("DONE — OrderServiceErrors alert: fires when order_errors_total increases")
bullet("DONE — ServiceDown alert: fires when any Prometheus target goes down")
bullet("DONE — OrderServiceHighLatency alert: fires when p95 latency exceeds 1 second")
bullet("DONE — Histogram metrics added to Order Service (order_request_duration_seconds)")
bullet("DONE — Services crash at startup if JWT_SECRET or DB_PASS not set")
bullet("DONE — allowed_ssh_cidr has no default — terraform apply requires explicit value")
bullet("TODO — Add DB connection retry with exponential backoff")
bullet("TODO — Configure Grafana notification channel (email/Slack) for alert delivery")
bullet("TODO — Restrict allowed_ssh_cidr to specific IP in production deployment")

pb()

# ═══════════════════════════════════════════════
# ASSIGNMENT 5 — TERRAFORM
# ═══════════════════════════════════════════════
h1("ASSIGNMENT 5 — Infrastructure as Code (Terraform + AWS)")

h2("Overview")
body(
    "The cloud infrastructure for MicroShop was provisioned using Terraform with the AWS provider. "
    "Terraform is a declarative IaC tool — the entire infrastructure is described in .tf files "
    "and created, updated, or destroyed with single commands. This makes infrastructure reproducible, "
    "version-controlled, and auditable."
)

h2("Implementation: Two Phases")
body(
    "During development, Terraform was first configured with a local Docker provider "
    "(kreuzwerker/docker) to validate the configuration structure locally. "
    "This phase is visible in screenshots 13_terraform_apply_*. "
    "After the professor confirmed that cloud deployment was required, the configuration "
    "was migrated to the AWS provider. The final AWS deployment is shown in screenshots "
    "14_terraform_apply_after_AWS_implementation_*. "
    "The code in the repository reflects the final AWS configuration only."
)
note(
    "AWS apply created: EC2 instance at 34.238.137.187 (us-east-1), "
    "security group sg-0091acf407323802f."
)

h2("Terraform Files")

h3("main.tf")
body(
    "Defines two AWS resources. aws_security_group opens inbound ports for SSH (22), HTTP (80), "
    "Grafana (3000), and Prometheus (9090). SSH and monitoring ports use the allowed_ssh_cidr "
    "variable — this variable has no default, so terraform apply fails if not explicitly set. "
    "aws_instance provisions a t3.micro EC2 VM with Amazon Linux 2. The user_data script "
    "installs Docker, git, and docker-compose on first boot. "
    "key_name accepts an optional SSH key pair via the ssh_key_name variable."
)

h3("variables.tf")
body(
    "Declares five variables: aws_region, instance_type, ami_id, allowed_ssh_cidr (no default — "
    "forces explicit security decision), and ssh_key_name (optional, empty = no SSH key). "
    "Removing the default from allowed_ssh_cidr was a deliberate security hardening step — "
    "it prevents accidental open-internet deployments."
)

h3("terraform.tfvars")
body(
    "Provides actual values: us-east-1, t3.micro, Amazon Linux 2 AMI, and allowed_ssh_cidr = "
    "0.0.0.0/0 for this assignment demo. t3.micro was chosen because t2.micro was rejected by "
    "AWS as not free-tier eligible. The 0.0.0.0/0 value is intentional for demo access and "
    "documented with a comment explaining it must be restricted in production."
)

h3("outputs.tf")
body(
    "Outputs after apply: instance_public_ip, instance_public_dns, grafana_url, "
    "prometheus_url, and security_group_id — making deployed services accessible "
    "without manually looking up the IP in the AWS Console."
)

h2("Terraform Screenshots")
fig("11a_terraform_init.png",   "terraform init — AWS provider downloaded successfully")
fig("11b_aws_credentials.png",  "AWS IAM credentials configured for Terraform authentication")
fig("12_terraform_plan_0.png",  "terraform plan — aws_security_group and aws_instance to be created")
fig("12_terraform_plan_1.png",  "terraform plan — EC2 instance configuration detail")
fig("14_terraform_apply_after_AWS_implementation_0.png", "terraform apply — EC2 instance creation in progress")
fig("14_terraform_apply_after_AWS_implementation_1.png", "terraform apply — security group created")
fig("14_terraform_apply_after_AWS_implementation_2.png", "terraform apply — outputs: public IP 34.238.137.187")

h2("Why Terraform over Manual AWS Console")
bullet("Reproducible — identical infrastructure on every terraform apply")
bullet("Version controlled — infrastructure changes tracked in git")
bullet("Self-documenting — .tf files describe exactly what exists and why")
bullet("Automated — no manual clicking, no missed steps")
bullet("Destroyable — terraform destroy removes everything, preventing surprise AWS charges")

pb()

# ═══════════════════════════════════════════════
# DEPLOYMENT GUIDE
# ═══════════════════════════════════════════════
h1("Deployment Guide")

h2("Prerequisites")
bullet("Docker Desktop installed and running")
bullet("Terraform >= 1.0 installed")
bullet("AWS account with IAM user (AdministratorAccess, access key + secret key)")
bullet("Git")

h2("1. Clone and Configure")
body("git clone https://github.com/Nurlybek-Nurzhan/Assignment_4-5_SRE.git")
body("cd Assignment_4-5_SRE")
body("cp .env.example .env  # then edit .env with your secrets")

h2("2. Run Locally")
body("docker compose up --build")
body("Dashboard: http://localhost:80  |  Prometheus: http://localhost:9090  |  Grafana: http://localhost:3000")
body("Login with credentials from .env (default: nurzhan / password123).")

h2("3. Provision AWS Infrastructure")
body("cd terraform")
body("Set allowed_ssh_cidr in terraform.tfvars to your IP (e.g. 203.0.113.5/32)")
body("Configure credentials: edit ~/.aws/credentials with your IAM access key")
body("terraform init && terraform plan && terraform apply")

h2("4. Simulate the Incident")
body("In docker-compose.yml change DB_HOST: postgres  →  DB_HOST: wrong-host")
body("docker compose up -d --force-recreate order-service")
body("Watch dashboard, check /health, observe order_errors_total in Prometheus.")

h2("5. Recover")
body("Restore DB_HOST: postgres in docker-compose.yml")
body("docker compose up -d --force-recreate order-service")

h2("6. Clean Up AWS")
body("cd terraform && terraform destroy")

# ═══════════════════════════════════════════════
# SAVE
# ═══════════════════════════════════════════════
doc.save(OUTPUT)
print(f"Saved: {OUTPUT}")
