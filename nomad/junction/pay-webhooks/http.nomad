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

variable "traefik_headers_accesscontrolalloworiginlist" {
  type = string
}

variable "traefik_headers_accessControlAllowHeaders" {
  type = string
}

variable "count" {
  type = number
}

job "pay-webhooks-http" {
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
      port "prometheus" {}
    }

    scaling {
      enabled = false
      min     = 1
      max     = 20
    }

    service {
      name = "pay-webhooks-${var.environment}"
      port = "http"
      tags = [
        "http",
        "traefik.enable=true",
        "traefik.consulcatalog.connect=true",
        "traefik.http.middlewares.pay-webhooks-${var.environment}-cors-headers.headers.accesscontrolalloworiginlist=${var.traefik_headers_accesscontrolalloworiginlist}",
        "traefik.http.middlewares.pay-webhooks-${var.environment}-cors-headers.headers.accessControlAllowHeaders=${var.traefik_headers_accessControlAllowHeaders}",
        "traefik.http.middlewares.pay-webhooks-${var.environment}-cors-headers.headers.addvaryheader=true",
        "traefik.http.routers.pay-webhooks-${var.environment}.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.pay-webhooks-${var.environment}.rule=Host(`${var.traefik_host_URL}`)",
        "traefik.http.routers.pay-webhooks-${var.environment}.middlewares=pay-webhooks-${var.environment}-cors-headers",
      ]

      connect {
        sidecar_service {
          proxy {
            upstreams {
              local_bind_port  = 8040
              destination_name = "payments-${var.environment}"
            }
          }
        }
      }

      check {
        type     = "http"
        path     = "/health"
        interval = "10s"
        timeout  = "2s"
      }
    }

    service {
      name = "pay-webhooks-${var.environment}"
      port = "prometheus"
      tags = ["metrics"]

      check {
        type     = "http"
        path     = "/"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "http" {
      driver = "docker"

      vault {
        policies = ["pay-webhooks-${var.environment}"]
      }

      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
PAYMENTS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_payments-${var.environment}"))}}
{{ with secret "kv/data/${var.environment}/pay-webhooks" }}
SECRET_KEY={{ .Data.data.secret_key }}
{{ end }}
EOH
      }

      config {
        image = var.docker_image
        ports = ["http", "prometheus"]
        args = [
          "http",
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {
        ENV_NAME              = "${var.environment}"
        FORWARDED_ALLOWED_IPS = "0.0.0.0"
        HTTP_ADDRESS          = "0.0.0.0"
        HTTP_PORT             = "${NOMAD_PORT_http}"
        SENTRY_DSN            = "https://aa58fc6a35984c71a157b35134bdf583@sentry.snowfall.se/156"
        PROMETHEUS_PORT       = "${NOMAD_PORT_prometheus}"
      }
    }
  }
}
