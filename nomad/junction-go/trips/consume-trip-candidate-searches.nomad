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

variable "max_trip_length_factor" {
  type = number
}

job "junction-go-trips-consume-trip-candidate-searches" {
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

  group "consume-trip-candidate-searches" {
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
      name = "consume-trip-candidate-searches-${var.environment}"
      port = "prometheus"
      tags = ["metrics"]

      connect {
        sidecar_service {
          proxy {
            upstreams {
              local_bind_port  = 8021
              destination_name = "planner-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8071
              destination_name = "offers-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8040
              destination_name = "schedules-${var.environment}"
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

    task "consume-trip-candidate-searches" {
      driver = "docker"

      template {
        data        = <<EOH
AMQP_DSN={{range $index, $service := service "amqp-${var.environment}"}}amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}// {{end}}
REDIS_DSN={{range $index, $service := service "redis-${var.environment}"}}redis://{{.Address}}:{{.Port}}// {{end}}
MONGO_DSN={{range $index, $service := service "mongodb-${var.environment}"}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}
PLANNER_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_planner-${var.environment}"))}}
OFFERS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_offers-${var.environment}"))}}
SCHEDULES_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_schedules-${var.environment}"))}}
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = var.docker_image
        ports = ["prometheus"]
        args = [
          "consume-trip-candidate-searches",
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {
        ENV_NAME               = "${var.environment}"
        SENTRY_DSN             = "https://9f6821dca30141bd8f3dc919b7806f6c@sentry.snowfall.se/26"
        PROMETHEUS_PORT        = "${NOMAD_PORT_prometheus}"
        MAX_TRIP_LENGTH_FACTOR = "${var.max_trip_length_factor}"
      }
    }
  }
}
