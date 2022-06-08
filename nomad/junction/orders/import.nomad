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

job "orders-import" {
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

  group "import" {
    count = 2
    network {
      mode = "bridge"
    }

    service {
      name = "orders-import-${var.environment}"
      tags = ["grpc"]
      connect {
        sidecar_service {
          proxy {
            upstreams {
              local_bind_port  = 9090
              destination_name = "passenger-name-records"
            }
          }
        }
      }
    }
    task "import" {
      driver = "docker"

      template {
        data        = <<EOH
AMQP_DSN={{range $index, $service := service (printf "amqp-${var.environment}")}}amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}// {{end}}
MONGO_DSN={{range $index, $service := service (printf "mongodb-${var.environment}")}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}
PASSENGER_NAME_RECORDS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_passenger-name-records_${var.environment}"))}}
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = var.docker_image
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
        ENV_NAME   = "${var.environment}"
        SENTRY_DSN = "https://7c600c1c458d403e8047091398239f20@sentry.snowfall.se/30"
      }
    }
  }
}
