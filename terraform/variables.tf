variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type (t3.micro is free tier eligible)"
  type        = string
  default     = "t3.micro"
}

variable "ami_id" {
  description = "Amazon Linux 2 AMI ID for us-east-1"
  type        = string
  default     = "ami-0c02fb55956c7d316"
}

variable "allowed_ssh_cidr" {
  description = "CIDR block allowed to SSH into the instance. Restrict to your IP in production."
  type        = string
  default     = "0.0.0.0/0"
}

variable "ssh_key_name" {
  description = "Name of the AWS key pair for SSH access. Leave empty to skip SSH key (demo only)."
  type        = string
  default     = ""
}
