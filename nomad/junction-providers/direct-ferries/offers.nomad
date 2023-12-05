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

variable "api_url" {
  type = string
}

variable "api_timeout" {
  type = string
}

variable "client_id" {
  type = string
}

variable "partner_code" {
  type = string
}

variable "affiliate_api_url" {
  type = string
}

variable "provider_company_id" {
  type = string
}

job "junction-providers-direct-ferries-offers" {
  datacenters = ["${var.datacenter}"]
  type        = "service"

  update {
    max_parallel      = 1
    auto_revert       = true
    auto_promote      = true
    canary            = 1
    healthy_deadline  = "2m"
    progress_deadline = "4m"
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
      name = "${JOB}-${var.environment}"
      port = "prometheus"
      tags = ["metrics"]

      connect {
        sidecar_service {}
      }

      check {
        type     = "http"
        path     = "/"
        interval = "30s"
        timeout  = "4s"
      }
    }
    task "offers" {
      driver = "docker"
      vault {
        policies = ["direct-ferries-${var.environment}"]
      }

      template {
        data        = <<EOH
AMQP_DSN={{range $index, $service := service "amqp-${var.environment}"}}amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}// {{end}}
REDIS_DSN={{range $index, $service := service "redis-${var.environment}"}}redis://{{.Address}}:{{.Port}}// {{end}}
{{ with secret "kv/data/${var.environment}/direct-ferries" }}
CLIENT_SECRET={{ .Data.data.client_secret }}
{{ end }}
RESELLER_PROVIDERS={{keyOrDefault "${var.environment}/providers/reseller-providers" "{}" | toJSON }}
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
        SENTRY_DSN          = "https://8375ccf16be441df8c8a5c04743d3f96@sentry.snowfall.se/59"
        PROMETHEUS_PORT     = "${NOMAD_PORT_prometheus}"
        PARTNER_CODE        = "${var.partner_code}"
        CLIENT_ID           = "${var.client_id}"
        AFFILIATE_API_URL   = "${var.affiliate_api_url}"
        API_URL             = "${var.api_url}"
        PROVIDER_COMPANY_ID = "${var.provider_company_id}"
        API_TIMEOUT         = "${var.api_timeout}"
      }
    }
  }
}
