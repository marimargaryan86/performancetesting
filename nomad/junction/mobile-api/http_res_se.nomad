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

job "res-se-mobile-api-http" {
  datacenters = ["${var.datacenter}"]
  type        = "service"

  update {
    max_parallel      = 1
    auto_revert       = true
    auto_promote      = true
    canary            = 1
    healthy_deadline  = "1m"
    progress_deadline = "2m"
  }

  group "http" {
    count = 3

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

    service {
      name = "res-se-mobile-api-${var.environment}"
      port = "http"
      tags = [
        "http",
        "traefik.enable=true",
        "traefik.consulcatalog.connect=true",
        "traefik.http.routers.res-se-mobile-api.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.res-se-mobile-api.rule=Host(`${var.traefik_host_URL}`)",
      ]

      connect {
        sidecar_service {
          proxy {
            upstreams {
              local_bind_port  = 8020
              destination_name = "currencies-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8070
              destination_name = "client-api-${var.environment}"
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
      name = "res-se-mobile-api-${var.environment}"
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
        memory = 600
        cpu    = 350
      }

      vault {
        policies = ["mobile-api-${var.environment}", "res-se-mobile-api-${var.environment}"]
      }
      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
CURRENCIES_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_currencies-${var.environment}"))}}
JUNCTION_API_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_client-api-${var.environment}"))}}
MONGO_DSN={{range $index, $service := service "mongodb-${var.environment}"}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}
REDIS_DSN={{range $index, $service := service "redis-${var.environment}"}}redis://{{.Address}}:{{.Port}}// {{end}}
SMTP_DSN={{range $index, $service := service "smtp"}}smtp://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}{{end}}
{{ with secret "kv/data/${var.environment}/mobile-api" }}
JUNCTION_API_TOKEN={{ .Data.data.junction_api_token }}
JWT_TOKEN_VERSION={{ .Data.data.jwt_token_version }}
JWT_PRIVATE_KEY={{ .Data.data.jwt_private_key }}
JWT_PUBLIC_KEY={{ .Data.data.jwt_public_key }}
{{ end }}
{{ with secret "kv/data/${var.environment}/res-se-mobile-api" }}
CLIENT_NAME={{ .Data.data.client_name }}
STRIPE_API_KEY={{ .Data.data.stripe_api_key }}
CREATE_STRIPE_CUSTOMERS={{ .Data.data.create_stripe_customers }}
SUPPORT_EMAIL={{ .Data.data.support_email }}
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
        ENV_NAME                        = "${var.environment}"
        FORWARDED_ALLOWED_IPS           = "0.0.0.0"
        HTTP_ADDRESS                    = "0.0.0.0"
        HTTP_PORT                       = "${NOMAD_PORT_http}"
        JWT_TOKEN_VERSION               = "1.0.0"
        SENTRY_DSN                      = "https://6166193e2bc24153b87e9bfca3d510d4@sentry.snowfall.se/38"
        PROMETHEUS_PORT                 = "${NOMAD_PORT_prometheus}"
        MONGO_DB                        = "res-se-mobile-api"
        VALIDATE_RESPONSES_AGAINST_SPEC = false
      }
    }
  }
}
