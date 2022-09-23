variable "docker_image" {
  type = string
}

variable "registry_address" {
  type = string
}

variable "registry_password" {
  type = string
}

variable "registry_username" {
  type = string
}

variable "environment" {
  type = string
}

variable "datacenter" {
  type = string
}

variable "traefik_entrypoints" {
  type = string
}

variable "traefik_host_URL" {
  type = string
}

job "pay-web" {
  datacenters = ["${var.datacenter}"]
  type        = "service"

  update {
    max_parallel      = 1
    auto_revert       = true
    auto_promote      = true
    canary            = 1
    healthy_deadline  = "30s"
    progress_deadline = "1m"
  }

  group "http" {
    count = 1

    network {
      port "http" {}
    }

    service {
      name = "pay-web-${var.environment}"
      port = "http"
      tags = [
        "traefik.enable=true",
        "traefik.http.routers.pay-web.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.pay-web.rule=Host(`${var.traefik_host_URL}`)",
      ]

      check {
        type     = "http"
        path     = "/"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "http" {
      driver = "docker"

      config {
        image = var.docker_image
        ports = ["http"]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {
        ENV_NAME = "${var.environment}"
        PORT     = "${NOMAD_PORT_http}"
      }
    }
  }
}
