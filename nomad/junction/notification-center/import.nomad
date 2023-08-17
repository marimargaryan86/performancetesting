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

job "notification-center-import" {
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
      name = "notification-center-import-${var.environment}"
      port = "prometheus"
      tags = ["metrics"]

      connect {
        sidecar_service {
          proxy {
            upstreams {
              local_bind_port  = 8010
              destination_name = "notifications-${var.environment}"
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
        policies = ["notification-center-${var.environment}"]
      }

      template {
        data        = <<EOH
REDIS_DSN={{range $index, $service := service "redis-${var.environment}"}}redis://{{.Address}}:{{.Port}}// {{end}}
AMQP_DSN={{range $index, $service := service "amqp-${var.environment}"}}amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}// {{end}}
NOTIFICATIONS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_notifications-${var.environment}"))}}
{{ with secret "kv/data/${var.environment}/notification-center" }}
TWILIO_SID={{ .Data.data.twilio_sid }}
TWILIO_TOKEN={{ .Data.data.twilio_token }}
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
          "import",
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {
        ENV_NAME        = "${var.environment}"
        SENTRY_DSN      = "https://060c09da336f4c0db7f7d87b8ccb5095@sentry.snowfall.se/162"
        PROMETHEUS_PORT = "${NOMAD_PORT_prometheus}"
        REDIS_PREFIX    = "junction-plus"
      }
    }
  }
}
