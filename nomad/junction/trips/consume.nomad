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

job "trips-consume" {
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

  group "consume" {
    count = 5
    network {
      mode = "bridge"
    }
    service {
      name = "trips-consume-${var.environment}"
      connect {
        sidecar_service {
          proxy {
            upstreams {
              local_bind_port  = 7070
              destination_name = "planner-${var.environment}"
            }
          }
        }
      }
    }

    task "consume" {
      driver = "docker"

      template {
        data        = <<EOH
AMQP_DSN={{range $index, $service := service (printf "amqp-${var.environment}")}}amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}// {{end}}
MONGO_DSN={{range $index, $service := service (printf "mongodb-${var.environment}")}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}

PLANNER_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_planner-${var.environment}"))}}
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = var.docker_image
        args = [
          "consume",
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {
        ENV_NAME   = "${var.environment}"
        SENTRY_DSN = "https://9f6821dca30141bd8f3dc919b7806f6c@sentry.snowfall.se/26"
      }
    }
  }
}
