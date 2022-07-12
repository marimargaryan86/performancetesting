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

job "pay-api-http" {
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
      name = "pay-api-${NOMAD_NAMESPACE}"
      port = "http"
      tags = [
        "http",
        "traefik.enable=true",
        "traefik.http.routers.pay-api.entrypoints=websecure",
        "traefik.http.routers.pay-api.rule=Host(`api.pay.junction.dev`)",
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
        policies = ["pay-api-development"]
      }

      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
{{ with secret (printf "kv/data/%s/pay-api" (env "NOMAD_NAMESPACE")) }}
CC_LOGIN={{ .Data.data.cc_login }}
CC_API_KEY={{ .Data.data.cc_api_key }}
CC_ENV={{ .Data.data.cc_env }}
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
        SENTRY_DSN            = "https://025704ebb5d24063b1153935db50ffd5@sentry.snowfall.se/42"
      }
    }
  }
}
