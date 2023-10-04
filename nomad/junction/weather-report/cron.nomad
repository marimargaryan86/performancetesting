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

job "weather-report-cron" {
  datacenters = ["${var.datacenter}"]
  type        = "batch"

  periodic {
    cron             = "0 * * * *"
    prohibit_overlap = true
  }

  group "cron" {
    count = 1

    restart {
      attempts = 3
      delay    = "5m"
      interval = "20m"
      mode     = "delay"
    }

    network {
      mode = "bridge"
      port "prometheus" {}
    }

    service {
      name = "weather-report-cron-${var.environment}"
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

    task "cron" {
      driver = "docker"

      template {
        data        = <<EOH
NOTIFICATIONS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_notifications-${var.environment}"))}}
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = var.docker_image
        args = [
          "cron"
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }


      env {
        ENV_NAME   = "${var.environment}"
        SENTRY_DSN = "https://193a30c8aed74d2993051f0f406470ce@sentry.snowfall.se/170"
      }
    }
  }
}
