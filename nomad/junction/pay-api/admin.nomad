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

variable "cc_address" {
  type = string
}

job "pay-api-admin" {
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

  group "admin" {
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
      name = "pay-api-admin-${var.environment}"
      port = "http"
      tags = [
        "http",
        "traefik.enable=true",
        "traefik.consulcatalog.connect=true",
        "traefik.http.middlewares.pay-api-admin-${var.environment}-cors-headers.headers.accesscontrolalloworiginlist=${var.traefik_headers_accesscontrolalloworiginlist}",
        "traefik.http.middlewares.pay-api-admin-${var.environment}-cors-headers.headers.accessControlAllowHeaders=${var.traefik_headers_accessControlAllowHeaders}",
        "traefik.http.middlewares.pay-api-admin-${var.environment}-cors-headers.headers.addvaryheader=true",
        "traefik.http.routers.pay-api-admin-${var.environment}.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.pay-api-admin-${var.environment}.rule=Host(`${var.traefik_host_URL}`)",
        "traefik.http.routers.pay-api-admin-${var.environment}.middlewares=pay-api-admin-${var.environment}-cors-headers",
      ]

      connect {
        sidecar_service {
          proxy {
            upstreams {
              local_bind_port  = 8030
              destination_name = "authentication-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8040
              destination_name = "companies-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8050
              destination_name = "pay-payments-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8060
              destination_name = "transactions-${var.environment}"
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
      name = "pay-api-admin-${var.environment}"
      port = "prometheus"
      tags = ["metrics"]

      check {
        type     = "http"
        path     = "/"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "admin" {
      driver = "docker"

      vault {
        policies = ["currencycloud-${var.environment}", "pay-api-${var.environment}"]
      }

      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
MONGO_DSN={{range $index, $service := service "mongodb-${var.environment}"}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}
REDIS_DSN={{range $index, $service := service "redis-${var.environment}"}}redis://{{.Address}}:{{.Port}}// {{end}}
AUTHENTICATION_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_authentication-${var.environment}"))}}
COMPANIES_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_companies-${var.environment}"))}}
PAYMENTS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_pay-payments-${var.environment}"))}}
TRANSACTIONS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_transactions-${var.environment}"))}}
{{ with secret "kv/data/${var.environment}/currencycloud" }}
CC_LOGIN={{ .Data.data.cc_login }}
CC_API_KEY={{ .Data.data.cc_api_key }}
CC_ENV={{ .Data.data.cc_env }}
{{ end }}
{{ with secret "kv/data/${var.environment}/pay-api" }}
JWT_PUBLIC_KEY={{ .Data.data.jwt_public_key }}
{{ end }}
EOH
      }

      config {
        image = var.docker_image
        ports = ["http", "prometheus"]
        args = [
          "admin-http",
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
        SENTRY_DSN            = "https://025704ebb5d24063b1153935db50ffd5@sentry.snowfall.se/42"
        PROMETHEUS_PORT       = "${NOMAD_PORT_prometheus}"
        CURRENCIES            = "AUD JPY SAR BHD KES SGD BGN KWD ZAR CAD SEK CNY CHF CZK NZD THB DKK NOK TRY EUR OMR UGX HKD GBP HUF PLN AED QAR USD RON ILS"
        CC_ADDRESS            = "${var.cc_address}"
      }
    }
  }
}
