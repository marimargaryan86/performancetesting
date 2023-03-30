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

variable "payer_company_id" {
  type = string
}

variable "payer_currency_code" {
  type = string
}

variable "use_pay_for_currency_conversions" {
  type = bool
}

variable "pay_admin_api_base_url" {
  type = string
}

variable "api_pay_base_url" {
  type = string
}

job "offers-import" {
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

    network {
      mode = "bridge"
      port "prometheus" {}
    }

    scaling {
      enabled = false
      min     = 1
      max     = 20
    }

    service {
      name = "offers-import-${var.environment}"
      port = "prometheus"
      tags = ["metrics"]

      connect {
        sidecar_service {}
      }

      check {
        type     = "http"
        path     = "/"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "import" {
      driver = "docker"

      vault {
        policies = ["offers-${var.environment}"]
      }


      template {
        data        = <<EOH
AMQP_DSN={{range $index, $service := service "amqp-${var.environment}"}}amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}// {{end}}
MONGO_DSN={{range $index, $service := service "mongodb-${var.environment}"}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}
REDIS_DSN={{range $index, $service := service "redis-${var.environment}"}}redis://{{.Address}}:{{.Port}}// {{end}}
{{ with secret "kv/data/${var.environment}/offers" }}
PAY_ADMIN_USERNAME={{ .Data.data.pay_admin_username }}
PAY_ADMIN_PASSWORD={{ .Data.data.pay_admin_password }}
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
        ENV_NAME                         = "${var.environment}"
        SENTRY_DSN                       = "https://7c600c1c458d403e8047091398239f20@sentry.snowfall.se/27"
        PROMETHEUS_PORT                  = "${NOMAD_PORT_prometheus}"
        PAYER_COMPANY_ID                 = "${var.payer_company_id}"
        PAYER_CURRENCY_CODE              = "${var.payer_currency_code}"
        USE_PAY_FOR_CURRENCY_CONVERSIONS = "${var.use_pay_for_currency_conversions}"
        PUBLIC_PAY_ADMIN_API_DSN         = "${var.pay_admin_api_base_url}"
        PUBLIC_PAY_API_DSN               = "${var.api_pay_base_url}"
      }
    }
  }
}
