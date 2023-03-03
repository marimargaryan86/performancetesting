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

variable "count" {
  type = number
}

variable "pay_admin_api_base_url" {
  type = string
}

job "hub-web-http" {
  datacenters = ["${var.datacenter}"]
  type        = "service"

  update {
    max_parallel      = 1
    auto_revert       = true
    auto_promote      = true
    canary            = 1
    healthy_deadline  = "60s"
    progress_deadline = "2m"
  }

  group "http" {
    count = "${var.count}"

    restart {
      attempts = 3
      delay    = "15s"
      interval = "10m"
      mode     = "delay"
    }

    network {
      mode = "bridge"
      port "http" {}
    }

    scaling {
      enabled = false
      min     = 1
      max     = 20
    }

    service {
      name = "hub-web-${var.environment}"
      port = "http"
      tags = [
        "traefik.enable=true",
        "traefik.consulcatalog.connect=true",
        "traefik.http.routers.hub-web-${var.environment}.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.hub-web-${var.environment}.rule=Host(`${var.traefik_host_URL}`)",
      ]

      connect {
        sidecar_service {}
      }

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
        ENV_NAME                      = "${var.environment}"
        PORT                          = "${NOMAD_PORT_http}"
        PUBLIC_PAY_ADMIN_API_BASE_URL = "${var.pay_admin_api_base_url}"
      }
    }
  }
}
