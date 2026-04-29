output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.microshop.public_ip
}

output "instance_public_dns" {
  description = "Public DNS of the EC2 instance"
  value       = aws_instance.microshop.public_dns
}

output "grafana_url" {
  description = "Grafana access URL"
  value       = "http://${aws_instance.microshop.public_ip}:3000"
}

output "prometheus_url" {
  description = "Prometheus access URL"
  value       = "http://${aws_instance.microshop.public_ip}:9090"
}

output "security_group_id" {
  description = "Security group ID"
  value       = aws_security_group.microshop_sg.id
}
