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

variable "traaefik_host_URL" {
  type = string
}

job "client-api-http" {
  datacenters = ["${var.datacenter}"]
  type        = "service"

  update {
    max_parallel      = 1
    auto_revert       = true
    auto_promote      = true
    canary            = 1
    healthy_deadline  = "30s"
    progress_deadline = "2m"
  }

  group "http" {
    count = 1

    network {
      port "http" {}
      port "prometheus" {}
    }

    service {
      name = "client-api-${var.environment}"
      port = "http"
      tags = [
        "http",
        "traefik.enable=true",
        "traefik.http.routers.client-api.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.client-api.rule=Host(`${var.traaefik_host_URL}`)",
      ]

      check {
        type     = "http"
        path     = "/health"
        interval = "10s"
        timeout  = "2s"
      }
    }

    service {
      name = "client-api-${var.environment}"
      port = "prometheus"
      tags = ["metrics"]

      check {
        type     = "http"
        path     = "/"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "http" {
      driver = "docker"

      vault {
        policies = ["client-api-${var.environment}"]
      }

      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
OFFERS_ADDRESS={{range $index, $service := service "grpc.offers-${var.environment}"}}{{.Address}}:{{.Port}} {{end}}
ORDERS_ADDRESS={{range $index, $service := service "grpc.orders-${var.environment}"}}{{.Address}}:{{.Port}} {{end}}
PLACES_ADDRESS={{range $index, $service := service "grpc.places-${var.environment}"}}{{.Address}}:{{.Port}} {{end}}
SCHEDULES_ADDRESS={{range $index, $service := service "grpc.schedules-${var.environment}"}}{{.Address}}:{{.Port}} {{end}}
TRIPS_ADDRESS={{range $index, $service := service "grpc.trips-${var.environment}"}}{{.Address}}:{{.Port}} {{end}}
{{ with secret "kv/data/${var.environment}/client-api" }}
JWT_PUBLIC_KEY={{ .Data.data.jwt_public_key }}
{{ end }}
EOH
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
        ENV_NAME              = "${var.environment}"
        FORWARDED_ALLOWED_IPS = "0.0.0.0"
        HTTP_ADDRESS          = "0.0.0.0"
        HTTP_PORT             = "${NOMAD_PORT_http}"
        JWT_TOKEN_VERSION     = "1.0.0"
        SENTRY_DSN            = "https://c674550aaa124dd9b5f02bf6c49b1983@sentry.snowfall.se/19"
        PROMETHEUS_PORT       = "${NOMAD_PORT_prometheus}"
      }
    }
  }
}
