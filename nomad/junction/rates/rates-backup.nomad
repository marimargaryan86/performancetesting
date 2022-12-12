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

job "rates-backup" {
  datacenters = ["${var.datacenter}"]
  type        = "batch"

  periodic {
    cron             = "@daily"
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

    task "backup_cron" {
      driver = "docker"

      vault {
        policies = ["rates-${var.environment}"]
      }

      template {
        data        = <<EOH
MONGO_DSN={{range $index, $service := service (printf "mongodb-%s" (env "NOMAD_NAMESPACE"))}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}
{{ with secret "kv/data/${var.environment}/rates" }}
BOUND_EMAIL={{ .Data.data.bound_email }}
BOUND_BASE_URL={{ .Data.data.bound_base_url }}
BOUND_PASSWORD={{ .Data.data.bound_password }}
API_LAYER_API_KEY={{ .Data.data.api_layer_api_key }}
API_LAYER_BASE_URL={{ .Data.data.api_layer_base_url }}
SOURCE_CURRENCIES={{ .Data.data.source_currencies }}
{{ end }}
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = var.docker_image
        args = [
          "backup_rates_cron"
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
      }
    }
  }
}
