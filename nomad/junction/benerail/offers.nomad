variable "docker_image" {
  type = string
}

variable "provider_company_id" {
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

variable "api_base_url" {
  type = string
}

job "benerail-offers" {
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

  group "offers" {
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
      name = "benerail-offers-${var.environment}"
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
    task "offers" {
      driver = "docker"
      vault {
        policies = ["benerail-${var.environment}"]
      }

      template {
        data        = <<EOH
AMQP_DSN={{range $index, $service := service "amqp-${var.environment}"}}amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}// {{end}}
MONGO_DSN={{range $index, $service := service "mongodb-${var.environment}"}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}
REDIS_DSN={{range $index, $service := service "redis-${var.environment}"}}redis://{{.Address}}:{{.Port}}// {{end}}
{{ with secret "kv/data/${var.environment}/benerail" }}
SUBSCRIPTION_KEY={{ .Data.data.subscription_key }}
CERT_BASE64={{ .Data.data.cert_base64 }}
RESELLER_PROVIDERS={{keyOrDefault "${var.environment}/providers/reseller-providers" "{}" | toJSON }}
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
          "offers",
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {
        ENV_NAME            = "${var.environment}"
        SENTRY_DSN          = "https://e0876a2d75114c40a4c5256919067373@sentry.snowfall.se/81"
        PROMETHEUS_PORT     = "${NOMAD_PORT_prometheus}"
        PROVIDER_COMPANY_ID = "${var.provider_company_id}"
        API_BASE_URL        = "${var.api_base_url}"
      }
    }
  }
}
