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

variable "traefik_entrypoints" {
  type = string
}

variable "traefik_host_URL" {
  type = string
}

variable "count" {
  type = number
}

variable "pay_admin_api_base_url" {
  type = string
}

variable "api_pay_base_url" {
  type = string
}

variable "client_api_base_url" {
  type = string
}

job "booking-hub-web-http" {
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

  group "http" {
    count = "${var.count}"

    restart {
      attempts = 3
      delay    = "15s"
      interval = "10m"
      mode     = "delay"
    }

    network {
      mode = "bridge"
      port "http" {}
    }

    scaling {
      enabled = false
      min     = 1
      max     = 20
    }

    service {
      name = "booking-hub-web-${var.environment}"
      port = "http"
      tags = [
        "traefik.enable=true",
        "traefik.consulcatalog.connect=true",
        "traefik.http.routers.booking-hub-web-${var.environment}.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.booking-hub-web-${var.environment}.rule=Host(`${var.traefik_host_URL}`)",
      ]

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

    task "http" {
      driver = "docker"

      vault {
        policies = ["hub-web-${var.environment}"]
      }

      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
{{ with secret "kv/data/${var.environment}/hub-web" }}
CLIENT_API_KEY={{ .Data.data.client_api_key }}
{{ end }}
EOH
      }

      config {
        image = var.docker_image
        ports = ["http"]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {
        ENV_NAME                      = "${var.environment}"
        PORT                          = "${NOMAD_PORT_http}"
        PUBLIC_PAY_ADMIN_API_BASE_URL = "${var.pay_admin_api_base_url}"
        PUBLIC_PAY_API_BASE_URL       = "${var.api_pay_base_url}"
        CLIENT_API_BASE_URL           = "${var.client_api_base_url}"
      }
    }
  }
}
