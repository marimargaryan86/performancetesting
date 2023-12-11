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

variable "zendesk_base_url" {
  type = string
}

job "junction-go-orders-consume-cancellations" {
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

  group consume-cancellations {
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
      name = "orders-consume-cancellations-${var.environment}"
      port = "prometheus"
      tags = ["metrics"]

      connect {
        sidecar_service {
          proxy {
            upstreams {
              local_bind_port  = 8010
              destination_name = "orders-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8020
              destination_name = "refunds-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8030
              destination_name = "junction-go-gateway-serve-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8040
              destination_name = "junction-go-resellers-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8050
              destination_name = "passenger-name-records-${var.environment}"
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
    task "consume-cancellations" {
      driver = "docker"

      vault {
        policies = ["zendesk-${var.environment}"]
      }

      template {
        data        = <<EOH
AMQP_DSN={{range $index, $service := service "amqp-${var.environment}"}}amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}// {{end}}
MONGO_DSN={{range $index, $service := service "mongodb-${var.environment}"}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}
REFUNDS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_refunds-${var.environment}"))}}
GATEWAY_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_junction-go-gateway-serve-${var.environment}"))}}
RESELLERS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_junction-go-resellers-${var.environment}"))}}
PASSENGER_NAME_RECORDS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_passenger-name-records-${var.environment}"))}}
{{ with secret "kv/data/${var.environment}/zendesk" }}
ZENDESK_CANCELLATION_GROUP_ID={{ .Data.data.cancellation_group_id }}
ZENDESK_API_KEY={{ .Data.data.zendesk_api_key }}
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
          "consume-cancellations",
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {
        ENV_NAME         = "${var.environment}"
        SENTRY_DSN       = "https://3b443c2609554d1db9fda2db77884fc9@sentry.snowfall.se/30"
        PROMETHEUS_PORT  = "${NOMAD_PORT_prometheus}"
        ZENDESK_BASE_URL = "${var.zendesk_base_url}"
      }
    }
  }
}
