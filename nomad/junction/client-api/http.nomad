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

job "client-api-http" {
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
      port "prometheus" {}
    }

    service {
      name = "client-api-${NOMAD_NAMESPACE}"
      port = "http"
      tags = [
        "http",
        "traefik.enable=true",
        "traefik.http.routers.client-api.entrypoints=websecure",
        "traefik.http.routers.client-api.rule=Host(`api.junction.dev`)",
      ]

      check {
        type     = "http"
        path     = "/health"
        interval = "10s"
        timeout  = "2s"
      }
    }

    service {
      name = "client-api-${NOMAD_NAMESPACE}"
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
        policies = ["client-api-development"]
      }

      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
OFFERS_ADDRESS={{range $index, $service := service (printf "grpc.offers-%s" (env "NOMAD_NAMESPACE"))}}{{.Address}}:{{.Port}} {{end}}
ORDERS_ADDRESS={{range $index, $service := service (printf "grpc.orders-%s" (env "NOMAD_NAMESPACE"))}}{{.Address}}:{{.Port}} {{end}}
PLACES_ADDRESS={{range $index, $service := service (printf "grpc.places-%s" (env "NOMAD_NAMESPACE"))}}{{.Address}}:{{.Port}} {{end}}
SCHEDULES_ADDRESS={{range $index, $service := service (printf "grpc.schedules-%s" (env "NOMAD_NAMESPACE"))}}{{.Address}}:{{.Port}} {{end}}
TRIPS_ADDRESS={{range $index, $service := service (printf "grpc.trips-%s" (env "NOMAD_NAMESPACE"))}}{{.Address}}:{{.Port}} {{end}}
{{ with secret (printf "kv/data/%s/client-api" (env "NOMAD_NAMESPACE")) }}
JWT_PUBLIC_KEY={{ .Data.data.jwt_public_key }}
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
        ENV_NAME              = "${NOMAD_NAMESPACE}"
        FORWARDED_ALLOWED_IPS = "0.0.0.0"
        HTTP_ADDRESS          = "0.0.0.0"
        HTTP_PORT             = "${NOMAD_PORT_http}"
        JWT_TOKEN_VERSION     = "1.0.0"
        SENTRY_DSN            = "https://c674550aaa124dd9b5f02bf6c49b1983@sentry.snowfall.se/19"
        PROMETHEUS_PORT       = "${NOMAD_PORT_prometheus}"
      }
    }
  }
}
