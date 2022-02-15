job "schedules" {
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

  group "import" {
    count = 1

    task "import" {
      driver = "docker"

      template {
        data        = <<EOH
AMQP_DSN="[{{range $index, $service := service "amqp"}}{{if ne $index 0}},{{end}}\"amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}//\"{{end}}]"
MONGO_DSN="[{{range $index, $service := service "mongodb"}}{{if ne $index 0}},{{end}}\"mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}}\"{{end}}]"
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = "${DOCKER_IMAGE}"
        args = [
          "import",
        ]

        auth {
          username       = "${NOMAD_REGISTRY_USERNAME}"
          password       = "${NOMAD_REGISTRY_PASSWORD}"
          server_address = "${CI_REGISTRY}"
        }
      }

      env {
        SENTRY_DSN = "https://4de05bbdaa1b4b58ab8401ad33ebac37@sentry.snowfall.se/20"
      }
    }
  }
}
