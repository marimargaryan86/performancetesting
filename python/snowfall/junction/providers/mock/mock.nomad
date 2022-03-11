job "mock" {
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

  group "offers" {
    count = 1

    task "offers" {
      driver = "docker"

      template {
        data        = <<EOH
AMQP_DSN="[{{range $index, $service := service "amqp"}}{{if ne $index 0}},{{end}}\"amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}//\"{{end}}]"
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = "${DOCKER_IMAGE}"
        args = [
          "offers",
        ]

        auth {
          username       = "${NOMAD_REGISTRY_USERNAME}"
          password       = "${NOMAD_REGISTRY_PASSWORD}"
          server_address = "${CI_REGISTRY}"
        }
      }

      env {
        ENV_NAME     = "junction.dev"
        SENTRY_DSN   = "https://e319b016d1b149299757a338479d7de7@sentry.snowfall.se/28"
      }
    }
  }
}
