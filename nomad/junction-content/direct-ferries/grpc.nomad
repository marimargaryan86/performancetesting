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

variable "api_base_url" {
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

job "junction-content-direct-ferries-grpc" {
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

  group "grpc" {
    count = "${var.count}"

    restart {
      attempts = 3
      delay    = "15s"
      interval = "10m"
      mode     = "delay"
    }

    network {
      mode = "bridge"
      port "grpc" {}
      port "prometheus" {}
    }

    scaling {
      enabled = false
      min     = 1
      max     = 20
    }

    service {
      name = "${JOB}-${var.environment}"
      port = "grpc"
      tags = ["grpc"]

      connect {
        sidecar_service {}
      }

      check {
        type     = "grpc"
        interval = "10s"
        timeout  = "2s"
      }
    }
    service {
      name = "${JOB}-${var.environment}"
      port = "prometheus"
      tags = ["metrics"]

      check {
        type     = "http"
        path     = "/"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "grpc" {
      driver = "docker"

      vault {
        policies = ["direct-ferries-${var.environment}"]
      }

      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
{{ with secret "kv/data/${var.environment}/direct-ferries" }}
CLIENT_SECRET={{ .Data.data.client_secret }}
{{ end }}
EOH
      }

      config {
        image = var.docker_image
        ports = ["grpc", "prometheus"]
        args = [
          "grpc",
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {
        ENV_NAME          = "${var.environment}"
        GRPC_ADDRESS      = "0.0.0.0"
        GRPC_PORT         = "${NOMAD_PORT_grpc}"
        SENTRY_DSN        = "https://35acfb4e991180b04b2b9e17fa87dddb@sentry.snowfall.se/233"
        PROMETHEUS_PORT   = "${NOMAD_PORT_prometheus}"
        PARTNER_CODE      = "${var.partner_code}"
        CLIENT_ID         = "${var.client_id}"
        AFFILIATE_API_URL = "${var.affiliate_api_url}"
        API_BASE_URL      = "${var.api_base_url}"
      }
    }
  }
}
