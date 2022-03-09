job "client-api" {
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

  group "client-api" {
    count = 1

    network {
      port "http" {}
    }

    service {
      name = "client-api"
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

    task "client-api" {
      driver = "docker"

      vault {
        policies = ["client-api-dev"]
      }

      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
PLACES_ADDRESS="[{{range $index, $service := service "grpc.places"}}{{if ne $index 0}},{{end}}\"{{.Address}}:{{.Port}}\"{{end}}]"
OFFERS_ADDRESS="[{{range $index, $service := service "grpc.offers"}}{{if ne $index 0}},{{end}}\"{{.Address}}:{{.Port}}\"{{end}}]"
{{ with secret "kv/dev/client-api" }}
{{ if .Data.data.jwt_public_key }}JWT_PUBLIC_KEY="{{ .Data.data.jwt_public_key }}"{{ end }}
{{ end }}
EOH 
      }

      config {
        image = "${DOCKER_IMAGE}"
        ports = ["http"]

        auth {
          username       = "${NOMAD_REGISTRY_USERNAME}"
          password       = "${NOMAD_REGISTRY_PASSWORD}"
          server_address = "${CI_REGISTRY}"
        }
      }

      env {
        FORWARDED_ALLOWED_IPS = "[\"0.0.0.0\"]"
        HTTP_ADDRESS          = "0.0.0.0"
        HTTP_PORT             = "${NOMAD_PORT_http}"
        JWT_TOKEN_VERSION     = "1.0.0"
        SENTRY_DSN            = "https://c674550aaa124dd9b5f02bf6c49b1983@sentry.snowfall.se/19"
      }
    }
  }
}
