terraform {
  required_version = ">= 1.5.0"
}

variable "service_name" {
  type    = string
  default = "dettrace-platform"
}

variable "container_port" {
  type    = number
  default = 8010
}

output "service_name" {
  value = var.service_name
}

output "container_port" {
  value = var.container_port
}
