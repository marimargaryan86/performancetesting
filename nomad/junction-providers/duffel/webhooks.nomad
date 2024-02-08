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

job "junction-providers-duffel-webhooks" {
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

  group "webhooks" {
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
      port "prometheus" {}
    }

    scaling {
      enabled = false
      min     = 1
      max     = 20
    }

    service {
      name = "duffel-webhooks-${var.environment}"
      port = "http"
      tags = [
        "http",
        "traefik.enable=true",
        "traefik.consulcatalog.connect=true",
        "traefik.http.routers.duffel-webhooks-${var.environment}.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.duffel-webhooks-${var.environment}.rule=Host(`${var.traefik_host_URL}`)"
      ]

      connect {
        sidecar_service {}
      }

      check {
        type     = "http"
        path     = "/health"
        interval = "30s"
        timeout  = "4s"
      }
    }

    service {
      name = "duffel-webhooks-${var.environment}"
      port = "prometheus"
      tags = ["metrics"]

      check {
        type     = "http"
        path     = "/"
        interval = "30s"
        timeout  = "4s"
      }
    }

    task "webhooks" {
      driver = "docker"
      vault {
        policies = ["duffel-${var.environment}"]
      }

      template {
        data        = <<EOH
{{ with secret "kv/data/${var.environment}/duffel" }}
WEBHOOK_SECRET={{ .Data.data.webhook_secret }}
{{ end }}
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = var.docker_image
        ports = ["http", "prometheus"]
        args = [
          "http",
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {
        ENV_NAME        = "${var.environment}"
        HTTP_ADDRESS    = "0.0.0.0"
        HTTP_PORT       = "${NOMAD_PORT_http}"
        SENTRY_DSN      = "https://c957bacb77d741509281e8b0a3b79e25@sentry.snowfall.se/57"
        PROMETHEUS_PORT = "${NOMAD_PORT_prometheus}"
      }
    }
  }
}
