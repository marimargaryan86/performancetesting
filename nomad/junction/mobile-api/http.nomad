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

variable "plus_api_address" {
  type = string
}

variable "plus_activated" {
  type = bool
}

variable "ory_client_token_endpoint" {
  type = string
}

variable "ory_client_id" {
  type = string
}

job "mobile-api-http" {
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
      name = "mobile-api-${var.environment}"
      port = "http"
      tags = [
        "http",
        "traefik.enable=true",
        "traefik.consulcatalog.connect=true",
        "traefik.http.routers.mobile-api-${var.environment}.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.mobile-api-${var.environment}.rule=Host(`${var.traefik_host_URL}`)",
      ]

      connect {
        sidecar_service {
          proxy {
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
      name = "mobile-api-${var.environment}"
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
      }

      vault {
        policies = ["mobile-api-${var.environment}"]
      }
      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
JUNCTION_API_ADDRESS={{(printf "http://%s" (env "NOMAD_UPSTREAM_ADDR_client-api-${var.environment}"))}}
MONGO_DSN={{range $index, $service := service "mongodb-${var.environment}"}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}
REDIS_DSN={{range $index, $service := service "redis-${var.environment}"}}redis://{{.Address}}:{{.Port}}// {{end}}
SMTP_DSN={{range $index, $service := service "smtp"}}smtp://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}{{end}}
{{ with secret "kv/data/${var.environment}/mobile-api" }}
JWT_PRIVATE_KEY={{ .Data.data.jwt_private_key }}
JWT_PUBLIC_KEY={{ .Data.data.jwt_public_key }}
STRIPE_API_KEY={{ .Data.data.stripe_api_key }}
ORY_CLIENT_SECRET={{ .Data.data.ory_client_secret }}
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
        ENV_NAME                  = "${var.environment}"
        FORWARDED_ALLOWED_IPS     = "0.0.0.0"
        HTTP_ADDRESS              = "0.0.0.0"
        HTTP_PORT                 = "${NOMAD_PORT_http}"
        JWT_TOKEN_VERSION         = "1.0.0"
        SENTRY_DSN                = "https://6166193e2bc24153b87e9bfca3d510d4@sentry.snowfall.se/38"
        PROMETHEUS_PORT           = "${NOMAD_PORT_prometheus}"
        MONGO_DB                  = "mobile-api"
        CLIENT_NAME               = "superApp"
        CREATE_STRIPE_CUSTOMERS   = true
        SUPPORT_EMAIL             = "support@diplomattravel.gr"
        PLUS_API_ADDRESS          = "${var.plus_api_address}"
        PLUS_ACTIVATED            = var.plus_activated
        ORY_CLIENT_TOKEN_ENDPOINT = var.ory_client_token_endpoint
        ORY_CLIENT_ID             = var.ory_client_id
      }
    }
  }
}
