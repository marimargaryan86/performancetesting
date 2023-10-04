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

variable "client_api_base_url" {
  type = string
}

variable "booking_hub_api_base_url" {
  type = string
}

variable "hub_api_base_url" {
  type = string
}

variable "ory_base_url" {
  type = string
}

job "hub-web-http" {
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
      name = "hub-web-${var.environment}"
      port = "http"
      tags = [
        "traefik.enable=true",
        "traefik.consulcatalog.connect=true",
        "traefik.http.routers.hub-web-${var.environment}.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.hub-web-${var.environment}.rule=Host(`${var.traefik_host_URL}`)",
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
PUBLIC_STRIPE_KEY={{ .Data.data.public_stripe_key }}
BOOKING_HUB_API_KEY={{ .Data.data.booking_hub_api_key }}
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
        ENV_NAME                 = "${var.environment}"
        PORT                     = "${NOMAD_PORT_http}"
        CLIENT_API_BASE_URL      = "${var.client_api_base_url}"
        BOOKING_HUB_API_BASE_URL = "${var.booking_hub_api_base_url}"
        ORY_BASE_URL             = "${var.ory_base_url}"
        HUB_API_BASE_URL         = "${var.hub_api_base_url}"
        PUBLIC_SENTRY_DSN        = "https://33b134d137c04fb8ba77aabdbd60304c@sentry.snowfall.se/68"
      }
    }
  }
}
