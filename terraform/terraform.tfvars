aws_region    = "us-east-1"
instance_type = "t3.micro"
ami_id        = "ami-0c02fb55956c7d316"

# Security: restrict to your IP in production e.g. "203.0.113.5/32"
# Left open for assignment demo purposes
allowed_ssh_cidr = "0.0.0.0/0"

# Set to your AWS key pair name to enable SSH access
# Left empty for assignment demo
ssh_key_name = ""
