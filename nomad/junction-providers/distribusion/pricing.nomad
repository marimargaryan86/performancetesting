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

variable "retailer_partner_number" {
  type = string
}

job "junction-providers-distribusion-pricing" {
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

  group "pricing" {
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

    task "pricing" {
      driver = "docker"
      vault {
        policies = ["distribusion-${var.environment}"]
      }

      template {
        data        = <<EOH
RATE_LIMITER_GRPC_HOST={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_rate-limiter-grpc-${var.environment}"))}}
RATE_LIMITER_SERVICE_CONFIGS={{keyOrDefault "${var.environment}/providers/distribusion/rate-limiter-service-configs" "{}" | toJSON }}
AMQP_DSN={{range $index, $service := service "amqp-${var.environment}"}}amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}// {{end}}
REDIS_DSN={{range $index, $service := service "redis-${var.environment}"}}redis://{{.Address}}:{{.Port}}// {{end}}
{{ with secret "kv/data/${var.environment}/distribusion" }}
API_KEY={{ .Data.data.api_key }}
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
          "pricing",
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {
        ENV_NAME                = "${var.environment}"
        SENTRY_DSN              = "https://81042716a3fa4b4fb9dc654b0fc5fd58@sentry.snowfall.se/56"
        PROMETHEUS_PORT         = "${NOMAD_PORT_prometheus}"
        PROVIDER_COMPANY_ID     = "${var.provider_company_id}"
        API_BASE_URL            = "${var.api_base_url}"
        RETAILER_PARTNER_NUMBER = "${var.retailer_partner_number}"
      }
    }
  }
}
