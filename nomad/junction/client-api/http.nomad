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

variable "traaefik_host_URL" {
  type = string
}

variable "count" {
  type = number
}

variable "validate_responses_against_spec" {
  type = bool
}

job "client-api-http" {
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
      name = "client-api-${var.environment}"
      port = "http"
      tags = [
        "http",
        "traefik.enable=true",
        "traefik.consulcatalog.connect=true",
        "traefik.http.routers.client-api-${var.environment}.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.client-api-${var.environment}.rule=Host(`${var.traaefik_host_URL}`)",
      ]

      connect {
        sidecar_service {
          proxy {
            upstreams {
              local_bind_port  = 8070
              destination_name = "offers-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8060
              destination_name = "orders-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8050
              destination_name = "places-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8040
              destination_name = "schedules-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8020
              destination_name = "trips-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8010
              destination_name = "authentication-${var.environment}"
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
      name = "client-api-${var.environment}"
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

      resources {
        cpu = 600
      }

      vault {
        policies = ["client-api-${var.environment}"]
      }

      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
OFFERS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_offers-${var.environment}"))}}
ORDERS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_orders-${var.environment}"))}}
PLACES_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_places-${var.environment}"))}}
SCHEDULES_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_schedules-${var.environment}"))}}
TRIPS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_trips-${var.environment}"))}}
AUTHENTICATION_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_authentication-${var.environment}"))}}
{{ with secret "kv/data/${var.environment}/client-api" }}
JWT_PUBLIC_KEY={{ .Data.data.jwt_public_key }}
{{ end }}
RESELLER_CURRENCIES={{keyOrDefault "${var.environment}/client-api/reseller-currencies" "{}" | toJSON }}
RESELLER_PAY_COMPANIES={{keyOrDefault "${var.environment}/client-api/reseller-pay-companies" "{}" | toJSON }}
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
        ENV_NAME                        = "${var.environment}"
        FORWARDED_ALLOWED_IPS           = "0.0.0.0"
        HTTP_ADDRESS                    = "0.0.0.0"
        HTTP_PORT                       = "${NOMAD_PORT_http}"
        JWT_TOKEN_VERSION               = "1.0.0"
        SENTRY_DSN                      = "https://c674550aaa124dd9b5f02bf6c49b1983@sentry.snowfall.se/19"
        PROMETHEUS_PORT                 = "${NOMAD_PORT_prometheus}"
        VALIDATE_RESPONSES_AGAINST_SPEC = "${var.validate_responses_against_spec}"
      }
    }
  }
}
