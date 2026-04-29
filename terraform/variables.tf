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
  description = "CIDR block allowed to SSH and monitoring ports. Set to your IP: e.g. 203.0.113.5/32"
  type        = string
}

variable "ssh_key_name" {
  description = "Name of the AWS key pair for SSH access. Leave empty to skip SSH key (demo only)."
  type        = string
  default     = ""
}
