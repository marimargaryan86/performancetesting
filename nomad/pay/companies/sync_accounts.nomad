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

variable "cc_address" {
  type = string
}

job "pay-companies-sync-accounts" {
  datacenters = ["${var.datacenter}"]
  type        = "batch"

  periodic {
    cron             = "@daily"
    prohibit_overlap = true
  }

  group "sync-accounts" {
    count = 1

    restart {
      attempts = 3
      delay    = "5m"
      interval = "20m"
      mode     = "delay"
    }

    task "sync-accounts" {
      driver = "docker"

      vault {
        policies = ["currencycloud-${var.environment}"]
      }

      template {
        data        = <<EOH
MONGO_DSN={{range $index, $service := service "mongodb-${var.environment}"}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}
{{ with secret "kv/data/${var.environment}/currencycloud" }}
CC_LOGIN={{ .Data.data.cc_login }}
CC_API_KEY={{ .Data.data.cc_api_key }}
{{ end }}
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = var.docker_image
        args = [
          "sync-accounts"
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }


      env {
        ENV_NAME   = "${var.environment}"
        SENTRY_DSN = "https://29671bbbf0174dc895a038d20b89d269@sentry.snowfall.se/157"
        CC_ADDRESS = var.cc_address
      }
    }
  }
}
