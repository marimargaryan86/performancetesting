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

variable "cc_address" {
  type = string
}

job "junction-hub-hub-api-http" {
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
      port "prometheus" {}
    }

    scaling {
      enabled = false
      min     = 1
      max     = 20
    }

    service {
      name = "hub-api-${var.environment}"
      port = "http"
      tags = [
        "http",
        "traefik.enable=true",
        "traefik.consulcatalog.connect=true",
        "traefik.http.routers.hub-api-${var.environment}.middlewares=hub-api-vpn-only-${var.environment}",
        "traefik.http.routers.hub-api-${var.environment}.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.hub-api-${var.environment}.rule=Host(`${var.traefik_host_URL}`)",
        "traefik.http.middlewares.hub-api-vpn-only-${var.environment}.ipwhitelist.sourcerange=52.56.69.33,13.42.170.234",
        "traefik.http.middlewares.hub-api-vpn-only-${var.environment}.ipwhitelist.ipstrategy.excludedips=172.16.0.0/16,10.255.0.0/16"
      ]

      connect {
        sidecar_service {
          proxy {
            upstreams {
              local_bind_port  = 8010
              destination_name = "authentication-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8020
              destination_name = "transactions-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8030
              destination_name = "currencies-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8040
              destination_name = "companies-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8060
              destination_name = "orders-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8070
              destination_name = "refunds-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8080
              destination_name = "resellers-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8090
              destination_name = "credit-card-payments-${var.environment}"
            }
            upstreams {
              local_bind_port  = 9000
              destination_name = "notifications-${var.environment}"
            }
          }
        }
      }

      check {
        type     = "http"
        path     = "/health"
        interval = "30s"
        timeout  = "4s"
      }
    }

    service {
      name = "hub-api-${var.environment}"
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
        policies = ["currencycloud-${var.environment}", "hub-api-${var.environment}"]
      }

      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
AUTHENTICATION_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_authentication-${var.environment}"))}}
ORDERS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_orders-${var.environment}"))}}
COMPANIES_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_companies-${var.environment}"))}}
TRANSACTIONS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_transactions-${var.environment}"))}}
CURRENCIES_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_currencies-${var.environment}"))}}
REFUNDS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_refunds-${var.environment}"))}}
RESELLERS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_resellers-${var.environment}"))}}
CREDIT_CARD_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_credit-card-payments-${var.environment}"))}}
NOTIFICATIONS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_notifications-${var.environment}"))}}
{{ with secret "kv/data/${var.environment}/hub-api" }}
STRIPE_API_KEY={{ .Data.data.stripe_api_key }}
{{ end }}
{{ with secret "kv/data/${var.environment}/currencycloud" }}
CC_LOGIN={{ .Data.data.cc_login }}
CC_API_KEY={{ .Data.data.cc_api_key }}
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
        SENTRY_DSN            = "https://7a9e03aa0fa24aed8155a1475b8be273@sentry.snowfall.se/147"
        PROMETHEUS_PORT       = "${NOMAD_PORT_prometheus}"
        CC_ADDRESS            = "${var.cc_address}"
      }
    }
  }
}
