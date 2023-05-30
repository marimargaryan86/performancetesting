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

job "orders-grpc" {
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
      name = "orders-${var.environment}"
      port = "grpc"
      tags = ["grpc"]

      connect {
        sidecar_service {
          proxy {
            upstreams {
              local_bind_port  = 8020
              destination_name = "passenger-name-records-${var.environment}"
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
      name = "orders-${var.environment}"
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

      template {
        data        = <<EOH
AMQP_DSN={{range $index, $service := service "amqp-${var.environment}"}}amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}// {{end}}
MONGO_DSN={{range $index, $service := service "mongodb-${var.environment}"}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}
PASSENGER_NAME_RECORDS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_passenger-name-records-${var.environment}"))}}
{{ with secret "kv/data/${var.environment}/zendesk" }}
ZENDESK_API_KEY={{ .Data.data.zendesk_api_key }}
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
        ENV_NAME         = "${var.environment}"
        GRPC_ADDRESS     = "0.0.0.0"
        GRPC_PORT        = "${NOMAD_PORT_grpc}"
        SENTRY_DSN       = "https://3b443c2609554d1db9fda2db77884fc9@sentry.snowfall.se/30"
        PROMETHEUS_PORT  = "${NOMAD_PORT_prometheus}"
        ZENDESK_BASE_URL = "${var.zendesk_base_url}"
      }
    }
  }
}
