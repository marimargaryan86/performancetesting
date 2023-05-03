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

job "rates-rates-backup" {
  datacenters = ["${var.datacenter}"]
  type        = "batch"

  periodic {
    cron             = "* * * * *"
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
        policies = ["rates-${var.environment}", "pay-api-${var.environment}"]
      }

      template {
        data        = <<EOH
REDIS_DSN={{range $index, $service := service "redis-${var.environment}"}}redis://{{.Address}}:{{.Port}}// {{end}}
MONGO_DSN={{range $index, $service := service (printf "mongodb-%s" (env "NOMAD_NAMESPACE"))}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}
{{ with secret "kv/data/${var.environment}/rates" }}
SOURCE_CURRENCIES={{ .Data.data.source_currencies }}
{{ end }}
{{ with secret "kv/data/${var.environment}/pay-api" }}
CC_LOGIN={{ .Data.data.cc_login }}
CC_API_KEY={{ .Data.data.cc_api_key }}
CC_ENV={{ .Data.data.cc_env }}
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
        CURRENCIES = "AUD JPY SAR BHD KES SGD BGN KWD ZAR CAD SEK CNY MXN CHF CZK NZD THB DKK NOK TRY EUR OMR UGX HKD GBP HUF PLN AED QAR USD RON ILS"
      }
    }
  }
}
