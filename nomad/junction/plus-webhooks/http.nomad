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

job "plus-webhooks-http" {
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
      port "prometheus" {}
    }

    scaling {
      enabled = false
      min     = 1
      max     = 20
    }

    service {
      name = "plus-webhooks-${var.environment}"
      port = "http"
      tags = [
        "http",
        "traefik.enable=true",
        "traefik.consulcatalog.connect=true",
        "traefik.http.routers.plus-webhooks-${var.environment}.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.plus-webhooks-${var.environment}.rule=Host(`${var.traefik_host_URL}`)"
      ]

      connect {
        sidecar_service {
          proxy {
            upstreams {
              local_bind_port  = 8010
              destination_name = "notifications-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8040
              destination_name = "flight-prediction-${var.environment}"
            }
          }
        }
      }

      check {
        type     = "http"
        path     = "/health"
        interval = "30s"
        timeout  = "4s"
      }
    }

    service {
      name = "plus-webhooks-${var.environment}"
      port = "prometheus"
      tags = ["metrics"]

      check {
        type     = "http"
        path     = "/"
        interval = "30s"
        timeout  = "4s"
      }
    }

    task "http" {
      driver = "docker"
      vault {
        policies = ["plus-webhooks-${var.environment}", "notification-center-${var.environment}", "poc-api-${var.environment}"]
      }

      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
REDIS_DSN={{range $index, $service := service "redis-${var.environment}"}}redis://{{.Address}}:{{.Port}}// {{end}}
NOTIFICATIONS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_notifications-${var.environment}"))}}
FLIGHT_PREDICTION_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_flight-prediction-${var.environment}"))}}
{{ with secret "kv/data/${var.environment}/plus-webhooks" }}
FLIGHT_STATS_APP_KEY={{ .Data.data.flight_stats_app_key }}
SHORTENER_KEY={{ .Data.data.shortener_key }}
{{ end }}
{{ with secret "kv/data/${var.environment}/notification-center" }}
TWILIO_SID={{ .Data.data.twilio_sid }}
TWILIO_TOKEN={{ .Data.data.twilio_token }}
{{ end }}
{{ with secret "kv/data/${var.environment}/poc-api" }}
OPENAI_API_KEY={{ .Data.data.openai_api_key }}
OPENAI_ORG={{ .Data.data.openai_org }}
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
        SENTRY_DSN            = "https://451b8cf11f0240d1884794af6d3d77f0@sentry.snowfall.se/165"
        PROMETHEUS_PORT       = "${NOMAD_PORT_prometheus}"
        REDIS_PREFIX          = "junction-plus"
        SHORTENER_DOMAIN      = "bdvp.short.gy"
        SHORTENER_URL         = "https://api.short.io/links"
        MATRIX_HOMESERVER_URL = "127.0.0.1:8008"
        MATRIX_TOKEN          = "..."
      }
    }
  }
}
