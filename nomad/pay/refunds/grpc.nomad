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

variable "cc_address" {
  type = string
}

job "refunds-grpc" {
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

    network {
      mode = "bridge"
      port "grpc" {}
    }

    scaling {
      enabled = false
      min     = 1
      max     = 20
    }

    service {
      name = "refunds-${var.environment}"
      port = "grpc"
      tags = ["grpc"]

      connect {
        sidecar_service {
          proxy {
            upstreams {
              local_bind_port  = 8020
              destination_name = "transactions-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8060
              destination_name = "orders-${var.environment}"
            }
          }
        }
      }

      check {
        type     = "grpc"
        interval = "30s"
        timeout  = "4s"
      }
    }

    task "grpc" {
      driver = "docker"

      vault {
        policies = ["currencycloud-${var.environment}", "webhooks-${var.environment}"]
      }

      template {
        data        = <<EOH
MONGO_DSN={{range $index, $service := service (printf "mongodb-%s" (env "NOMAD_NAMESPACE"))}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}
TRANSACTIONS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_transactions-${var.environment}"))}}
ORDERS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_orders-${var.environment}"))}}
{{ with secret "kv/data/${var.environment}/currencycloud" }}
CC_LOGIN={{ .Data.data.cc_login }}
CC_API_KEY={{ .Data.data.cc_api_key }}
{{ end }}
{{ with secret "kv/data/${var.environment}/webhooks" }}
STRIPE_API_KEY={{ .Data.data.stripe_api_key }}
{{ end }}
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = var.docker_image
        ports = ["grpc"]
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
        ENV_NAME     = "${var.environment}"
        GRPC_PORT    = "${NOMAD_PORT_grpc}"
        GRPC_ADDRESS = "0.0.0.0"
        CC_ADDRESS   = "${var.cc_address}"
        SENTRY_DSN   = "https://02028ad4684847638dc2a2413ad6faa5@sentry.snowfall.se/164"
      }
    }
  }
}
