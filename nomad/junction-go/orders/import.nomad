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

variable "use_pay_to_create_transaction" {
  type = bool
}

job "orders-import" {
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

  group "import" {
    count = "${var.count}"

    restart {
      attempts = 3
      delay    = "15s"
      interval = "10m"
      mode     = "delay"
    }

    scaling {
      enabled = false
      min     = 1
      max     = 20
    }

    network {
      mode = "bridge"
      port "prometheus" {}
    }

    service {
      name = "orders-import-${var.environment}"
      port = "prometheus"
      tags = ["metrics"]

      connect {
        sidecar_service {
          proxy {
            upstreams {
              local_bind_port  = 8020
              destination_name = "passenger-name-records-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8030
              destination_name = "transactions-${var.environment}"
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
    task "import" {
      driver = "docker"

      vault {
        policies = ["offers-${var.environment}"]
      }

      template {
        data        = <<EOH
AMQP_DSN={{range $index, $service := service "amqp-${var.environment}"}}amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}// {{end}}
MONGO_DSN={{range $index, $service := service "mongodb-${var.environment}"}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}
PASSENGER_NAME_RECORDS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_passenger-name-records-${var.environment}"))}}
TRANSACTIONS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_transactions-${var.environment}"))}}
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = var.docker_image
        ports = ["prometheus"]
        args = [
          "import",
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {
        ENV_NAME                      = "${var.environment}"
        SENTRY_DSN                    = "https://7c600c1c458d403e8047091398239f20@sentry.snowfall.se/30"
        PROMETHEUS_PORT               = "${NOMAD_PORT_prometheus}"
        USE_PAY_TO_CREATE_TRANSACTION = "${var.use_pay_to_create_transaction}"
      }
    }
  }
}
