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

job "transactions-reports-cron" {
  datacenters = ["${var.datacenter}"]
  type        = "batch"

  periodic {
    cron             = "0 18 * * SUN"
    prohibit_overlap = true
  }

  group "reports-cron" {
    count = 1

    restart {
      attempts = 3
      delay    = "5m"
      interval = "20m"
      mode     = "delay"
    }

    task "reports-cron" {
      driver = "docker"

      template {
        data        = <<EOH
SMTP_DSN={{range $index, $service := service "smtp"}}smtp://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}{{end}}
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = var.docker_image
        args = [
          "reports_cron"
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }


      env {
        ENV_NAME      = "${var.environment}"
        SENTRY_DSN    = "https://0c052cf147584d4391a5243202168e20@sentry.snowfall.se/153"
        PAY_EMAIL     = "pay@snowfalltravel.com"
        FINANCE_EMAIL = "finance@snowfalltravel.com"
      }
    }
  }
}
