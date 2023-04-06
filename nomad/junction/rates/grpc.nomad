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

job "rates-grpc" {
  datacenters = ["${var.datacenter}"]
  type        = "service"

  update {
    max_parallel      = 1
    auto_revert       = true
    auto_promote      = true
    canary            = 1
    healthy_deadline  = "1m"
    progress_deadline = "2m"
  }

  group "grpc" {
    count = "${var.count}"

    network {
      port "grpc" {}
    }

    scaling {
      enabled = false
      min     = 1
      max     = 20
    }

    service {
      name = "rates-${var.environment}"
      port = "grpc"
      tags = ["grpc"]

      check {
        type     = "grpc"
        interval = "30s"
        timeout  = "2s"
      }
    }

    task "grpc" {
      driver = "docker"

      template {
        data        = <<EOH
MONGO_DSN={{range $index, $service := service (printf "mongodb-%s" (env "NOMAD_NAMESPACE"))}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}
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
        SENTRY_DSN   = "https://0ab9747b3f7042d9882a664f0e31f229@sentry.snowfall.se/46"
      }
    }
  }
}
