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

variable "datacenter" {
  type = string
}

variable "traefik_entrypoints" {
  type = string
}

variable "traefik_host_URL" {
  type = string
}

job "engineering-http" {
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
    count = 1

    restart {
      attempts = 3
      delay    = "15s"
      interval = "10m"
      mode     = "delay"
    }

    network {
      mode = "bridge"
      port "http" {}
      port "prometheus" {}
    }

    scaling {
      enabled = false
      min     = 1
      max     = 20
    }

    service {
      name = "docs-engineering-${var.environment}"
      port = "http"
      tags = [
        "http",
        "traefik.enable=true",
        "traefik.http.middlewares.docs-engineering-vpn-only.ipwhitelist.sourcerange=52.56.69.33",
        "traefik.http.middlewares.docs-engineering-vpn-only.ipwhitelist.ipstrategy.excludedips.172.16.0.0/16",
        "traefik.http.routers.docs-engineering.middlewares=docs-engineering-vpn-only",
        "traefik.http.routers.docs-engineering-${var.environment}.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.docs-engineering-${var.environment}.rule=Host(`${var.traefik_host_URL}`)",
      ]
    }

    task "http" {
      driver = "docker"

      config {
        image = var.docker_image
        ports = ["http"]
        args = [
          "http",
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }
    }
  }
}
