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

      template {
        data        = <<EOH
PLACES_ADDRESS="[{{range $index, $service := service "grpc.places"}}{{if ne $index 0}},{{end}}\"{{.Address}}:{{.Port}}\"{{end}}]"
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
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
        HTTP_ADDRESS = "0.0.0.0"
        HTTP_PORT    = "${NOMAD_PORT_http}"
        SENTRY_DSN   = "https://c674550aaa124dd9b5f02bf6c49b1983@sentry.snowfall.se/19"
      }
    }
  }
}
