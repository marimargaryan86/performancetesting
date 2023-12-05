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

variable "count" {
  type = number
}

variable "api_base_url" {
  type = string
}

variable "http_timeout" {
  type = string
}

variable "bucket" {
  type = string
}

variable "email_recipient" {
  type = string
}

job "junction-providers-duffel-orders" {
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

  group "orders" {
    count = "${var.count}"

    restart {
      attempts = 3
      delay    = "15s"
      interval = "10m"
      mode     = "delay"
    }

    network {
      mode = "bridge"
      port "prometheus" {}
    }

    scaling {
      enabled = false
      min     = 1
      max     = 20
    }

    service {
      name = "${JOB}-${var.environment}"
      port = "prometheus"
      tags = ["metrics"]

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
        type     = "http"
        path     = "/"
        interval = "30s"
        timeout  = "4s"
      }
    }

    task "orders" {
      driver = "docker"

      vault {
        policies = ["duffel-${var.environment}"]
      }

      template {
        data        = <<EOH
RATE_LIMITER_GRPC_HOST={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_rate-limiter-grpc-${var.environment}"))}}
RATE_LIMITER_SERVICE_CONFIGS={{keyOrDefault "${var.environment}/providers/duffel/rate-limiter-service-configs" "{}" | toJSON }}
AMQP_DSN={{range $index, $service := service "amqp-${var.environment}"}}amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}// {{end}}
REDIS_DSN={{range $index, $service := service "redis-${var.environment}"}}redis://{{.Address}}:{{.Port}}// {{end}}
SMTP_DSN={{range $index, $service := service "smtp"}}smtp://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}{{end}}
{{ with secret "kv/data/${var.environment}/duffel" }}
API_KEY={{ .Data.data.api_key }}
RESELLERS_MAP={{ .Data.data.resellers_map }}
STORAGE_DSN=s3://{{ .Data.data.aws_access_key_id }}:{{ .Data.data.aws_secret_access_key | urlquery }}@/${var.bucket}/duffel
{{ end }}
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = var.docker_image
        ports = ["prometheus"]
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
        ENV_NAME        = "${var.environment}"
        SMTP_SENDER     = "sender@snowfalltravel.com"
        SMTP_RECIPIENT  = "${var.email_recipient}"
        PROMETHEUS_PORT = "${NOMAD_PORT_prometheus}"
        API_BASE_URL    = "${var.api_base_url}"
        SENTRY_DSN      = "https://c957bacb77d741509281e8b0a3b79e25@sentry.snowfall.se/57"
        HTTP_TIMEOUT    = "${var.http_timeout}"
      }
    }
  }
}
