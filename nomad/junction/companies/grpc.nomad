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

job "companies-grpc" {
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
      name = "companies-${var.environment}"
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
      name = "companies-${var.environment}"
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
        policies = ["currencycloud-${var.environment}"]
      }

      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
MONGO_DSN={{range $index, $service := service "mongodb-${var.environment}"}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}
{{ with secret "kv/data/${var.environment}/currencycloud" }}
CC_LOGIN={{ .Data.data.cc_login }}
CC_API_KEY={{ .Data.data.cc_api_key }}
CC_ENV={{ .Data.data.cc_env }}
{{ end }}
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
        ENV_NAME              = "${var.environment}"
        FORWARDED_ALLOWED_IPS = "0.0.0.0"
        GRPC_ADDRESS          = "0.0.0.0"
        GRPC_PORT             = "${NOMAD_PORT_grpc}"
        SENTRY_DSN            = "https://29671bbbf0174dc895a038d20b89d269@sentry.snowfall.se/157"
        PROMETHEUS_PORT       = "${NOMAD_PORT_prometheus}"
      }
    }
  }
}
