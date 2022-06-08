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

job "mobile-api-http" {
  datacenters = ["junction-dev-dc1"]
  type        = "service"

  update {
    max_parallel      = 1
    auto_revert       = true
    auto_promote      = true
    canary            = 1
    healthy_deadline  = "30s"
    progress_deadline = "2m"
  }

  group "http" {
    count = 1

    network {
      port "http" {}
    }

    service {
      name = "mobile-api-${NOMAD_NAMESPACE}"
      port = "http"
      tags = [
        "http",
        "traefik.enable=true",
        "traefik.http.routers.mobile-api.entrypoints=websecure",
        "traefik.http.routers.mobile-api.rule=Host(`superapp.junction.dev`)",
      ]

      check {
        type     = "http"
        path     = "/health"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "http" {
      driver = "docker"

      vault {
        policies = ["mobile-api-development"]
      }
      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
MONGO_DSN={{range $index, $service := service (printf "mongodb-%s" (env "NOMAD_NAMESPACE"))}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}
REDIS_DSN={{range $index, $service := service (printf "redis-%s" (env "NOMAD_NAMESPACE"))}}redis://{{.Address}}:{{.Port}}// {{end}}
SMTP_DSN={{range $index, $service := service "smtp"}}smtp://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}{{end}}
{{ with secret (printf "kv/%s/mobile-api" (env "NOMAD_NAMESPACE")) }}
JUNCTION_API_TOKEN={{ .Data.data.junction_api_token }}
JWT_TOKEN_VERSION={{ .Data.data.jwt_token_version }}
JWT_PRIVATE_KEY={{ .Data.data.jwt_private_key }}
JWT_PUBLIC_KEY={{ .Data.data.jwt_public_key }}
STRIPE_API_KEY={{ .Data.data.stripe_api_key }}
{{ end }}
EOH
      }

      config {
        image = var.docker_image
        ports = ["http"]
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
        ENV_NAME              = "${NOMAD_NAMESPACE}"
        FORWARDED_ALLOWED_IPS = "0.0.0.0"
        HTTP_ADDRESS          = "0.0.0.0"
        HTTP_PORT             = "${NOMAD_PORT_http}"
        JWT_TOKEN_VERSION     = "1.0.0"
        JUNCTION_API_ADDRESS  = "https://api.junction.dev"
        SENTRY_DSN            = "https://6166193e2bc24153b87e9bfca3d510d4@sentry.snowfall.se/38"
      }
    }
  }
}

