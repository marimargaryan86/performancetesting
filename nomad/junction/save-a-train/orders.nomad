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

job "save-a-train-orders" {
  datacenters = ["junction-dev-dc1"]
  type        = "service"

  update {
    max_parallel      = 1
    auto_revert       = true
    auto_promote      = true
    canary            = 1
    healthy_deadline  = "30s"
    progress_deadline = "2m"
  }

  group "orders" {
    count = 2

    network {
      port "grpc" {}
      mode ="bridge"

    }
    service {
      name = "save-a-train-orders-production"
      port = "grpc"
      tags = ["grpc"]
      connect {
        sidecar_service {
          proxy {
            upstreams {
              local_bind_port = 7070
              destination_name = "geodata-production"
            }
          }
        }
      }
    }

    task "orders" {
      driver = "docker"

      vault {
        policies = ["save-a-train-${var.environment}"]
      }

      template {
        data        = <<EOH
AMQP_DSN={{range $index, $service := service (printf "amqp-${var.environment}")}}amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}// {{end}}
GEODATA_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_geodata-${var.environment}"))}}
REDIS_DSN={{range $index, $service := service (printf "redis-${var.environment}")}}redis://{{.Address}}:{{.Port}}// {{end}}
{{ with secret (printf "kv/${var.environment}/save-a-train") }}
API_EMAIL={{ .Data.data.api_email }}
API_PASSWORD={{ .Data.data.api_password }}
API_SEARCH_PASSWORD={{ .Data.data.api_search_password }}
API_BOOKING_TOKEN={{ .Data.data.api_booking_token }}
{{ end }}
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = var.docker_image
        args = [
          "orders",
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {
        API_BASE_URL        = "https://satvendorstest.saveatrain.com/api/"
        API_SEARCH_BASE_URL = "https://apisearch.saveatrain.com/search"
        ENV_NAME            = "${var.environment}"
        SENTRY_DSN          = "https://f01c7c8bf4d04a709a65b4be8b11ba69@sentry.snowfall.se/36"
      }
    }
  }
}
