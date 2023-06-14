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

variable "provider_company_id" {
  type = string
}

variable "api_base_url" {
  type = string
}

variable "api_search_base_url" {
  type = string
}

job "save-a-train-grpc" {
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
      name = "save-a-train-${var.environment}"
      port = "grpc"
      tags = ["grpc"]

      connect {
        sidecar_service {}
      }

      check {
        type     = "grpc"
        interval = "10s"
        timeout  = "2s"
      }
    }
    service {
      name = "save-a-train-${var.environment}"
      port = "prometheus"
      tags = ["metrics"]

      check {
        type     = "http"
        path     = "/"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "grpc" {
      driver = "docker"

      vault {
        policies = ["save-a-train-${var.environment}"]
      }

      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
AMQP_DSN={{range $index, $service := service "amqp-${var.environment}"}}amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}// {{end}}
MONGO_DSN={{range $index, $service := service "mongodb-${var.environment}"}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}
REDIS_DSN={{range $index, $service := service "redis-${var.environment}"}}redis://{{.Address}}:{{.Port}}// {{end}}
{{ with secret "kv/data/${var.environment}/save-a-train" }}
  API_PASSWORD={{ .Data.data.api_password }}
  API_SEARCH_PASSWORD={{ .Data.data.api_search_password }}
  API_BOOKING_TOKEN={{ .Data.data.api_booking_token }}
{{ end }}
RESELLER_PROVIDERS={{keyOrDefault "${var.environment}/providers/reseller-providers" "{}" | toJSON }}
EOH
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
        ENV_NAME            = "${var.environment}"
        GRPC_ADDRESS        = "0.0.0.0"
        GRPC_PORT           = "${NOMAD_PORT_grpc}"
        SENTRY_DSN          = "https://f01c7c8bf4d04a709a65b4be8b11ba69@sentry.snowfall.se/36"
        PROMETHEUS_PORT     = "${NOMAD_PORT_prometheus}"
        PROVIDER_COMPANY_ID = "${var.provider_company_id}"
        API_BASE_URL        = "${var.api_base_url}"
        API_EMAIL           = "gb@snowfalltravel.com"
        API_SEARCH_BASE_URL = "${var.api_search_base_url}"
      }
    }
  }
}
