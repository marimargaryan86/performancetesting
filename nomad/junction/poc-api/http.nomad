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

job "poc-api-http" {
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
      port "prometheus" {}
    }

    scaling {
      enabled = false
      min     = 1
      max     = 20
    }

    service {
      name = "poc-api-${var.environment}"
      port = "http"
      tags = [
        "http",
        "traefik.enable=true",
        "traefik.http.routers.poc-api-${var.environment}.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.poc-api-${var.environment}.rule=Host(`${var.traefik_host_URL}`)",
      ]

      check {
        type     = "http"
        path     = "/health"
        interval = "10s"
        timeout  = "2s"
      }
    }

    service {
      name = "poc-api-${var.environment}"
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

      resources {
        cpu = 600
      }

      vault {
        policies = ["poc-api-${var.environment}"]
      }

      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
MONGO_DSN={{range $index, $service := service "mongodb-${var.environment}"}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}
REDIS_DSN={{range $index, $service := service "redis-${var.environment}"}}redis://{{.Address}}:{{.Port}}// {{end}}
{{ with secret "kv/data/${var.environment}/poc-api" }}
JUNCTION_API_TOKEN={{ .Data.data.junction_api_token }}
FLIGHT_STATS_APP_KEY={{ .Data.data.flight_stats_app_key }}
TWILIO_TOKEN={{ .Data.data.twilio_token }}
TWILIO_SID={{ .Data.data.twilio_sid }}
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
        ENV_NAME                        = "${var.environment}"
        FORWARDED_ALLOWED_IPS           = "0.0.0.0"
        HTTP_ADDRESS                    = "0.0.0.0"
        HTTP_PORT                       = "${NOMAD_PORT_http}"
        PROMETHEUS_PORT                 = "${NOMAD_PORT_prometheus}"
        VALIDATE_RESPONSES_AGAINST_SPEC = false
        MONGO_DB                        = "mobile-api"
        TWILIO_SENDER                   = "+15674831787"
        FLIGHT_STATS_APP_ID             = "4fb1a656"
        SENTRY_DSN                      = "https://edddac6f53a345bfa2b49ac386a69e9b@sentry.snowfall.se/80"
        JUNCTION_API_ADDRESS            = "https://api.junction.dev"
        FLIGHT_STATS_API_ADDRESS        = "https://api.flightstats.com/flex/flightstatus/rest/v2/json/flight/status/"
      }
    }
  }
}
