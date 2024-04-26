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

variable "xe_address" {
  type = string
}

job "pay-rates-rates-backup" {
  datacenters = ["${var.datacenter}"]
  type        = "batch"

  periodic {
    cron             = "0 * * * *"
    prohibit_overlap = true
  }

  group "rates-backup" {
    count = 1

    restart {
      attempts = 3
      delay    = "5m"
      interval = "20m"
      mode     = "delay"
    }

    task "rates-backup" {
      driver = "docker"

      vault {
        policies = ["xe-${var.environment}"]
      }

      template {
        data        = <<EOH
REDIS_DSN={{range $index, $service := service "redis-${var.environment}"}}redis://{{.Address}}:{{.Port}}// {{end}}
MONGO_DSN={{range $index, $service := service (printf "mongodb-%s" (env "NOMAD_NAMESPACE"))}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}
CACHE_TTL=8
{{ with secret "kv/data/${var.environment}/xe" }}
XE_LOGIN={{ .Data.data.xe_login }}
XE_API_KEY={{ .Data.data.xe_api_key }}
{{ end }}
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = var.docker_image
        args = [
          "backup-rates-cron"
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }


      env {
        ENV_NAME   = "${var.environment}"
        SENTRY_DSN = "https://0ab9747b3f7042d9882a664f0e31f229@sentry.snowfall.se/46"
        CURRENCIES = "SEK GBP EUR USD AED"
        XE_ADDRESS = var.xe_address
      }
    }
  }
}
