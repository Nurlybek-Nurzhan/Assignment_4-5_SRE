from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
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

def set_font(run, size=11, bold=False, color=None):
    run.font.name = "Calibri"
    run.font.size = Pt(size)
    run.font.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)

def heading(text, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14 if level == 1 else 8)
    p.paragraph_format.space_after  = Pt(4)
    run = p.add_run(text)
    sizes  = {1: 16, 2: 13, 3: 12}
    colors = {1: (31, 73, 125), 2: (31, 73, 125), 3: (0, 0, 0)}
    set_font(run, size=sizes.get(level, 11), bold=True, color=colors.get(level))
    return p

def body(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(5)
    run = p.add_run(text)
    set_font(run, size=11)
    return p

def note(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.left_indent = Cm(0.7)
    run = p.add_run(text)
    set_font(run, size=10, color=(100, 100, 100))
    return p

def bullet(text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(text)
    set_font(run, size=11)
    return p

def add_screenshot(filename, caption, width=15):
    path = os.path.join(SCREENSHOTS, filename)
    if os.path.exists(path):
        doc.add_picture(path, width=Cm(width))
        last = doc.paragraphs[-1]
        last.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp = doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp.paragraph_format.space_after = Pt(12)
        run = cp.add_run(f"Figure: {caption}")
        set_font(run, size=9, color=(120, 120, 120))
    else:
        p = doc.add_paragraph()
        run = p.add_run(f"[Screenshot not found: {filename}]")
        set_font(run, size=10, color=(200, 0, 0))

def page_break():
    doc.add_page_break()

# ══════════════════════════════════════════════════════════════
# TITLE PAGE
# ══════════════════════════════════════════════════════════════
for _ in range(4):
    doc.add_paragraph()

tp = doc.add_paragraph()
tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = tp.add_run("ASSIGNMENT 4–5 REPORT")
set_font(r, size=22, bold=True, color=(31, 73, 125))

doc.add_paragraph()
tp2 = doc.add_paragraph()
tp2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = tp2.add_run("Incident Response Simulation and\nInfrastructure as Code Implementation")
set_font(r2, size=14)

doc.add_paragraph()
tp3 = doc.add_paragraph()
tp3.alignment = WD_ALIGN_PARAGRAPH.CENTER
r3 = tp3.add_run("MicroShop — Containerized Microservices System")
set_font(r3, size=12, bold=True)

doc.add_paragraph()
tp4 = doc.add_paragraph()
tp4.alignment = WD_ALIGN_PARAGRAPH.CENTER
r4 = tp4.add_run("Introduction to SRE  |  2026")
set_font(r4, size=11, color=(100, 100, 100))

doc.add_paragraph()
tp5 = doc.add_paragraph()
tp5.alignment = WD_ALIGN_PARAGRAPH.CENTER
r5 = tp5.add_run("GitHub: https://github.com/Nurlybek-Nurzhan/Assignment_4-5_SRE")
set_font(r5, size=10, color=(31, 73, 125))

page_break()

# ══════════════════════════════════════════════════════════════
# SYSTEM OVERVIEW
# ══════════════════════════════════════════════════════════════
heading("System Overview", 1)
body(
    "MicroShop is a containerized e-commerce platform built to demonstrate SRE practices. "
    "It consists of five independent backend microservices, a PostgreSQL database, an Nginx "
    "frontend acting as a reverse proxy, Prometheus for metrics collection, and Grafana for "
    "visualization. All components run in Docker containers orchestrated by Docker Compose "
    "on a shared internal bridge network called microshop-net."
)

heading("Architecture", 2)
bullet("Auth Service (port 8001) — handles user login and returns a session token")
bullet("Product Service (port 8002) — serves the product catalog")
bullet("Order Service (port 8003) — manages orders, the only service with a PostgreSQL dependency")
bullet("User Service (port 8004) — manages user profiles")
bullet("Chat Service (port 8005) — handles user messaging")
bullet("PostgreSQL — persistent database, used exclusively by the Order Service")
bullet("Prometheus (port 9090) — scrapes /metrics from all five services every 15 seconds; alert rules defined")
bullet("Grafana (port 3000) — visualizes Prometheus metrics (admin/admin)")
bullet("Nginx (port 80) — serves the frontend and proxies all API calls via /api/* routes")

body(
    "The frontend calls all backend services through Nginx proxy_pass routes "
    "(/api/auth/, /api/products/, /api/orders/, /api/users/, /api/chat/). "
    "This approach resolves browser CORS restrictions and keeps backend ports internal."
)

heading("Known Limitations (Assignment Scope)", 2)
bullet("Auth service uses hardcoded users and returns a placeholder token — no real JWT implementation")
bullet("Product and Chat services use in-memory state — data resets on container restart")
bullet("Database credentials are hardcoded in docker-compose.yml — acceptable for a local assignment, not for production")
bullet("Security group opens all ports to 0.0.0.0/0 — sufficient for assignment demonstration, would be restricted in production")

heading("Running System", 2)
add_screenshot("1_terminal .png", "docker compose up — all 9 containers started successfully")
add_screenshot("2_docker_ps.png", "docker ps — all containers running with correct port mappings")

heading("Frontend Dashboard", 2)
body(
    "The MicroShop Dashboard shows real-time health of all five services. "
    "Green dots mean healthy. The dashboard fetches products from the Product Service "
    "and orders from the Order Service."
)
add_screenshot("3_frontend_dashboard.png", "MicroShop Dashboard — all 5 services healthy (green dots)")

heading("Monitoring", 2)
body(
    "Prometheus scrapes all five services at their /metrics endpoints. "
    "Alert rules are defined in alert_rules.yml — two alerts are configured: "
    "OrderServiceErrors (triggers when order_errors_total increases) and "
    "ServiceDown (triggers when any target becomes unreachable)."
)
add_screenshot("4_prometheus_targets.png", "Prometheus — all 5 service targets showing UP")
add_screenshot("5_grafana.png", "Grafana — connected to Prometheus data source")

page_break()

# ══════════════════════════════════════════════════════════════
# ASSIGNMENT 4 — INCIDENT REPORT
# ══════════════════════════════════════════════════════════════
heading("ASSIGNMENT 4 — Incident Response Simulation", 1)

heading("1. Incident Summary", 2)
body(
    "A production-level incident was simulated in the Order Service by deliberately setting "
    "the DB_HOST environment variable to an invalid hostname ('wrong-host'). After restarting "
    "the container with this broken configuration, the Order Service lost all database "
    "connectivity and began returning HTTP 503 errors on every request. All other services "
    "remained fully operational throughout the incident."
)

heading("2. Impact Assessment", 2)
bullet("Order Service: 100% unavailable — /orders and /health both returned HTTP 503")
bullet("Frontend dashboard: Order Service showed as 'Unreachable'")
bullet("Users could not view or create orders")
bullet("Auth, Product, User, and Chat services: fully operational (fault isolation confirmed)")
bullet("Data integrity: no data was lost — PostgreSQL remained healthy throughout")

heading("3. Severity Classification", 2)
body(
    "Severity: SEV-2 (Major) — a critical business function (order processing) was fully "
    "unavailable. Classified as SEV-2 rather than SEV-1 because the failure was isolated to "
    "one service and did not take down the entire platform."
)

heading("4. Timeline of Events", 2)
bullet("T+00:00 — DB_HOST changed from 'postgres' to 'wrong-host' in docker-compose.yml")
bullet("T+00:05 — Order Service restarted: docker compose up -d --force-recreate order-service")
bullet("T+00:10 — Frontend dashboard detected Order Service as 'Unreachable'")
bullet("T+00:15 — /orders endpoint began returning HTTP 503")
bullet("T+00:20 — order_errors_total counter started incrementing in Prometheus")
bullet("T+00:25 — /health returned 503: 'DB connection failed: could not translate host name wrong-host'")
bullet("T+00:30 — Docker logs confirmed: repeated psycopg2 connection errors to wrong-host:5432")
bullet("T+01:00 — Root cause identified: incorrect DB_HOST value in environment config")
bullet("T+01:05 — DB_HOST corrected back to 'postgres' in docker-compose.yml")
bullet("T+01:10 — Order Service restarted with corrected configuration")
bullet("T+01:15 — /health returned HTTP 200: db: connected")
bullet("T+01:20 — Frontend dashboard: all services green, full recovery confirmed")

heading("Incident Evidence", 2)
add_screenshot("6_incident_dashboard.png",
    "Dashboard during incident — Order Service 'Unreachable', 503 errors visible in browser Network tab")
add_screenshot("7_incident_prometheus.png",
    "Prometheus during incident — note: /metrics endpoint still responded (service process was running), "
    "but /health showed DB failure. This demonstrates a key SRE lesson: a service can be 'up' in Prometheus "
    "but functionally broken — process liveness ≠ service health.")
add_screenshot("8a_incident_logs.png",
    "Docker logs — repeated DB connection errors: could not translate host name 'wrong-host'")
add_screenshot("8b_incident_metrics_and_health.png",
    "/health returning 503 and order_errors_total incrementing in /metrics")

heading("5. Root Cause Analysis", 2)
body(
    "Root cause: misconfigured DB_HOST environment variable. "
    "Docker Compose services resolve each other by container name on the internal network. "
    "The container name 'postgres' resolves correctly via Docker DNS. "
    "The value 'wrong-host' has no DNS record on the microshop-net network, so every "
    "call to psycopg2.connect() immediately raised an OperationalError. "
    "The service has no retry logic — each request attempted a fresh connection with a "
    "3-second timeout, failed, incremented order_errors_total, and returned 503."
)
body(
    "Secondary observation: Prometheus showed the service as UP during the incident because "
    "the /metrics endpoint (which does not touch the database) continued to respond. "
    "This highlights why dependency health checks in /health endpoints are essential — "
    "they expose functional failures that raw process liveness cannot detect."
)

heading("6. Mitigation Steps", 2)
bullet("Identified the failing container: docker logs order-service")
bullet("Confirmed the bad value: inspected DB_HOST in docker-compose.yml")
bullet("Applied fix: changed DB_HOST back to 'postgres'")
bullet("Restarted only the affected container: docker compose up -d --force-recreate order-service")
bullet("Verified via /health endpoint and frontend dashboard")

heading("7. Resolution Confirmation", 2)
body(
    "Full recovery achieved within ~70 seconds of applying the fix. "
    "The /health endpoint returned HTTP 200 with db: connected, "
    "the frontend showed all green, and the order_errors_total counter stopped incrementing."
)
add_screenshot("9_recovery_dashboard.png",
    "Recovery — all services green, Order Service showing DB: connected")
add_screenshot("10a_recovery_logs.png",
    "Recovery logs — HTTP 200 responses confirmed after fix")
add_screenshot("10b_recovery_metrics_and_health.png",
    "/health returning 200 with db: connected after DB_HOST corrected")

page_break()

# ══════════════════════════════════════════════════════════════
# POSTMORTEM
# ══════════════════════════════════════════════════════════════
heading("Postmortem Analysis", 1)

heading("1. Incident Overview", 2)
body(
    "On 2026-04-29, the MicroShop Order Service became fully unavailable for approximately "
    "70 seconds due to an incorrect database hostname in the service environment configuration. "
    "The incident was intentionally introduced as part of Assignment 4 to simulate a realistic "
    "production failure and practice the full incident response cycle."
)

heading("2. Customer Impact", 2)
bullet("100% of order-related requests failed with HTTP 503 during the incident window")
bullet("Order viewing and creation were completely unavailable")
bullet("Product browsing, authentication, user profiles, and chat were unaffected")
bullet("No data loss — PostgreSQL remained healthy and all existing orders were preserved")

heading("3. Root Cause Analysis", 2)
body(
    "The DB_HOST environment variable was manually set to a non-existent hostname. "
    "In Docker Compose, services discover each other through Docker's internal DNS using "
    "container names as hostnames. When DB_HOST='wrong-host', every database call failed "
    "at the DNS resolution step before even attempting a TCP connection to PostgreSQL. "
    "The service had no retry mechanism or connection pooling, so failures were immediate and total."
)

heading("4. Detection and Response Evaluation", 2)
body(
    "Detection was fast — the frontend dashboard showed the failure within 10 seconds of "
    "the restart, and the /health endpoint provided an exact error message pointing to the "
    "bad hostname. Prometheus metrics confirmed the error pattern through order_errors_total."
)
body(
    "One gap identified: Prometheus showed the service as UP throughout because it scrapes "
    "/metrics, which does not require a database connection. In a production environment, "
    "Prometheus alert rules should monitor both process liveness (up) and functional health "
    "(via health check endpoints or error rate thresholds). The OrderServiceErrors alert rule "
    "added to alert_rules.yml directly addresses this."
)

heading("5. Resolution Summary", 2)
body(
    "A single configuration change (correcting DB_HOST to 'postgres') followed by a container "
    "restart fully restored the service. Resolution time: under 2 minutes. No code changes, "
    "no data recovery, and no other services required any intervention."
)

heading("6. Lessons Learned", 2)
bullet("Environment variables are a common and dangerous source of misconfiguration in containerized systems")
bullet("A service being 'up' in Prometheus does not mean it is functionally healthy — dependency checks matter")
bullet("The /health endpoint design (checking actual DB connectivity) was correct and proved essential for diagnosis")
bullet("Microservices fault isolation worked as designed — one broken service did not cascade")
bullet("Manual changes to running service configuration should always be validated before applying")

heading("7. Action Items", 2)
bullet("DONE — Added Prometheus alert rules: OrderServiceErrors and ServiceDown in monitoring/alert_rules.yml")
bullet("Add startup validation to Order Service — fail fast with a clear error if DB_HOST cannot be resolved at boot")
bullet("Implement connection retry with exponential backoff in psycopg2 calls")
bullet("Add Grafana alerting channel (email/Slack) connected to Prometheus alerts")
bullet("Replace hardcoded DB credentials in docker-compose.yml with a .env file")
bullet("Add healthcheck blocks to FastAPI service containers in docker-compose.yml")

page_break()

# ══════════════════════════════════════════════════════════════
# ASSIGNMENT 5 — TERRAFORM
# ══════════════════════════════════════════════════════════════
heading("ASSIGNMENT 5 — Infrastructure as Code (Terraform + AWS)", 1)

heading("Overview", 2)
body(
    "The cloud infrastructure for MicroShop was provisioned using Terraform with the AWS provider. "
    "Terraform is a declarative IaC tool — infrastructure is described in .tf files and created, "
    "updated, or destroyed with single commands. This makes infrastructure reproducible, "
    "version-controlled, and auditable, unlike manual AWS Console clicks."
)

heading("Implementation Note: Two Phases", 2)
body(
    "During development, Terraform was first configured with a local Docker provider "
    "(kreuzwerker/docker) to provision containers locally. This was later replaced with "
    "the AWS provider after the professor confirmed cloud deployment was required. "
    "The screenshots labeled 13_terraform_apply_* show the Docker provider phase. "
    "The screenshots labeled 14_terraform_apply_after_AWS_implementation_* show the final "
    "AWS deployment that created a real EC2 instance."
)
note(
    "The Terraform code in the repository (main.tf) reflects the final AWS configuration only. "
    "The AWS apply created: EC2 instance at 34.238.137.187, security group sg-0091acf407323802f."
)

heading("Terraform Files", 2)

heading("main.tf", 3)
body(
    "Defines two AWS resources. First, aws_security_group creates a firewall with inbound rules "
    "for SSH (22), HTTP (80), Grafana (3000), and Prometheus (9090), with all outbound traffic "
    "allowed. Second, aws_instance provisions a t3.micro EC2 virtual machine using the "
    "Amazon Linux 2 AMI. The user_data script runs on first boot and installs Docker, "
    "so the application can be deployed immediately after the instance starts."
)

heading("variables.tf", 3)
body(
    "Declares three input variables: aws_region, instance_type, and ami_id. "
    "Using variables instead of hardcoded values makes the configuration reusable — "
    "changing the region or instance size requires editing only terraform.tfvars."
)

heading("terraform.tfvars", 3)
body(
    "Provides the actual values: us-east-1, t3.micro, ami-0c02fb55956c7d316 (Amazon Linux 2 for us-east-1). "
    "t3.micro was chosen because it is free-tier eligible — t2.micro was initially used but "
    "was rejected by AWS as not free-tier eligible in the selected region."
)

heading("outputs.tf", 3)
body(
    "Defines what Terraform prints after apply: instance_public_ip, instance_public_dns, "
    "grafana_url (http://<ip>:3000), prometheus_url (http://<ip>:9090), and security_group_id. "
    "These outputs make it easy to access deployed services without looking up the IP manually."
)

heading("Deployment Commands", 2)
bullet("terraform init — downloads the hashicorp/aws provider plugin, initializes the working directory")
bullet("terraform plan — previews all changes before applying; shows exact resources to be created")
bullet("terraform apply — creates resources on AWS (completed in ~30 seconds)")
bullet("terraform destroy — removes all provisioned resources cleanly to avoid ongoing AWS charges")

heading("Terraform Screenshots", 2)
add_screenshot("11a_terraform_init.png",
    "terraform init — AWS provider (hashicorp/aws v5.x) downloaded successfully")
add_screenshot("11b_aws_credentials.png",
    "AWS IAM credentials configured for Terraform authentication")
add_screenshot("12_terraform_plan_0.png",
    "terraform plan — showing aws_security_group and aws_instance to be created")
add_screenshot("12_terraform_plan_1.png",
    "terraform plan — EC2 instance configuration detail (AMI, instance type, user_data)")
add_screenshot("14_terraform_apply_after_AWS_implementation_0.png",
    "terraform apply (AWS) — EC2 instance creation in progress")
add_screenshot("14_terraform_apply_after_AWS_implementation_1.png",
    "terraform apply (AWS) — resources created: security group sg-0091acf407323802f")
add_screenshot("14_terraform_apply_after_AWS_implementation_2.png",
    "terraform apply (AWS) — outputs: public IP 34.238.137.187, Grafana and Prometheus URLs")

heading("Why Terraform over Manual AWS Console", 2)
bullet("Reproducible — running terraform apply again produces identical infrastructure every time")
bullet("Version controlled — infrastructure changes are tracked in git alongside application code")
bullet("Documented — .tf files are human-readable and self-documenting")
bullet("Automated — no manual clicking, no typos, no forgotten steps")
bullet("Destroyable — terraform destroy cleanly removes all resources, preventing surprise AWS charges")

page_break()

# ══════════════════════════════════════════════════════════════
# DEPLOYMENT GUIDE
# ══════════════════════════════════════════════════════════════
heading("Deployment Guide", 1)

heading("Prerequisites", 2)
bullet("Docker Desktop installed and running")
bullet("Terraform >= 1.0 installed")
bullet("AWS account with IAM user (access key + secret key, AdministratorAccess policy)")
bullet("Git")

heading("1. Clone the Repository", 2)
body("git clone https://github.com/Nurlybek-Nurzhan/Assignment_4-5_SRE.git")
body("cd Assignment_4-5_SRE")

heading("2. Run the Application Locally", 2)
body("docker compose up --build")
body("Dashboard: http://localhost:80  |  Prometheus: http://localhost:9090  |  Grafana: http://localhost:3000 (admin/admin)")

heading("3. Provision AWS Infrastructure", 2)
body("cd terraform")
body("aws configure  # enter your IAM access key, secret key, region: us-east-1")
body("terraform init")
body("terraform plan")
body("terraform apply")
body("Terraform outputs the public IP. SSH into the instance and run docker compose up to deploy.")

heading("4. Simulate the Incident", 2)
body("In docker-compose.yml, change DB_HOST: postgres  →  DB_HOST: wrong-host")
body("docker compose up -d --force-recreate order-service")
body("Observe Order Service become Unreachable in the dashboard. Check Prometheus for order_errors_total.")

heading("5. Recover", 2)
body("Restore DB_HOST: postgres in docker-compose.yml")
body("docker compose up -d --force-recreate order-service")
body("All services return to healthy state within ~10 seconds.")

heading("6. Clean Up AWS Resources", 2)
body("cd terraform && terraform destroy")
body("This removes the EC2 instance and security group. Always run this after the assignment to avoid AWS charges.")

# ══════════════════════════════════════════════════════════════
# SAVE
# ══════════════════════════════════════════════════════════════
doc.save(OUTPUT)
print(f"Report saved to: {OUTPUT}")
