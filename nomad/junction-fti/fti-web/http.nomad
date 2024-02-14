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

job "junction-fti-fti-web-http" {
  datacenters = ["${var.datacenter}"]
  type        = "service"

  update {
    max_parallel      = 1
    auto_revert       = true
    auto_promote      = true
    canary            = 1
    healthy_deadline  = "2m"
    progress_deadline = "4m"
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
      name = "fti-web-${var.environment}"
      port = "http"
      tags = [
        "traefik.enable=true",
        "traefik.consulcatalog.connect=true",
        "traefik.http.routers.fti-web-${var.environment}.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.fti-web-${var.environment}.rule=Host(`${var.traefik_host_URL}`)",
      ]

      connect {
        sidecar_service {}
      }

      check {
        type     = "http"
        path     = "/"
        interval = "30s"
        timeout  = "4s"
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
        ENV_NAME          = "${var.environment}"
        PORT              = "${NOMAD_PORT_http}"
        PUBLIC_SENTRY_DSN = "https://ef15f1238446cd1d5c38ab2890633241@sentry.snowfall.se/234"
      }
    }
  }
}

