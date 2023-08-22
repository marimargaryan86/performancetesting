variable "docker_image" {
  type = string
}

variable "provider_company_id" {
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

variable "count" {
  type = number
}

variable "api_base_url" {
  type = string
}

variable "api_booking_base_url" {
  type = string
}

variable "bucket" {
  type = string
}

job "ask2go-grpc" {
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

  group "grpc" {
    count = "${var.count}"

    restart {
      attempts = 3
      delay    = "15s"
      interval = "10m"
      mode     = "delay"
    }

    network {
      mode = "bridge"
      port "grpc" {}
      port "prometheus" {}
    }

    scaling {
      enabled = false
      min     = 1
      max     = 20
    }

    service {
      name = "ask2go-${var.environment}"
      port = "grpc"
      tags = ["grpc"]

      connect {
        sidecar_service {
          proxy {
            upstreams {
              local_bind_port  = 9081
              destination_name = "rate-limiter-grpc-${var.environment}"
            }
          }
        }
      }

      check {
        type     = "grpc"
        interval = "10s"
        timeout  = "2s"
      }
    }

    service {
      name = "ask2go-grpc-${var.environment}"
      port = "prometheus"
      tags = ["metrics"]

      check {
        type     = "http"
        path     = "/"
        interval = "30s"
        timeout  = "4s"
      }
    }
    task "grpc" {
      driver = "docker"
      vault {
        policies = ["ask2go-${var.environment}"]
      }

      template {
        data        = <<EOH
RATE_LIMITER_GRPC_HOST={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_rate-limiter-grpc-${var.environment}"))}}
RATE_LIMITER_SERVICE_CONFIGS={{keyOrDefault "${var.environment}/providers/ask2go/rate-limiter-service-configs" "{}" | toJSON }}
AMQP_DSN={{range $index, $service := service "amqp-${var.environment}"}}amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}// {{end}}
MONGO_DSN={{range $index, $service := service (printf "mongodb-%s" (env "NOMAD_NAMESPACE"))}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}
REDIS_DSN={{range $index, $service := service "redis-${var.environment}"}}redis://{{.Address}}:{{.Port}}// {{end}}
RESELLER_PROVIDERS={{keyOrDefault "${var.environment}/providers/reseller-providers" "{}" | toJSON }}
{{ with secret "kv/data/${var.environment}/ask2go" }}
STORAGE_DSN=s3://{{ .Data.data.aws_access_key_id }}:{{ .Data.data.aws_secret_access_key | urlquery }}@/${var.bucket}/ask2go
{{ end }}
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = var.docker_image
        ports = ["grpc", "prometheus"]
        args = [
          "grpc",
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {
        ENV_NAME                  = "${var.environment}"
        GRPC_ADDRESS              = "0.0.0.0"
        GRPC_PORT                 = "${NOMAD_PORT_grpc}"
        SENTRY_DSN                = "https://c299617e39d446ccb1053a04d9ac12b8@sentry.snowfall.se/34"
        PROMETHEUS_PORT           = "${NOMAD_PORT_prometheus}"
        PROVIDER_COMPANY_ID       = "${var.provider_company_id}"
        POLL_RETRIES_LIMIT        = "60"
        WAIT_TIME_BETWEEN_POLLING = "2"
        API_BASE_URL              = "${var.api_base_url}"
        API_BOOKING_BASE_URL      = "${var.api_booking_base_url}"
      }
    }
  }
}
