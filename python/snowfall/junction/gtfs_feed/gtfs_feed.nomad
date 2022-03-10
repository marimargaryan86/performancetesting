job "gtfs-feed" {
  datacenters = ["junction-dev-dc1"]
  type        = "batch"

  periodic {
    cron             = "@weekly"
    prohibit_overlap = true
  }

  group "france-intercity" {
    count = 1

    ephemeral_disk {
      size = 1000
    }

    task "france-intercity" {
      driver = "docker"

      template {
        data        = <<EOH
AMQP_DSN="[{{range $index, $service := service "amqp"}}{{if ne $index 0}},{{end}}\"amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}//\"{{end}}]"
MONGO_DSN="[{{range $index, $service := service "mongodb"}}{{if ne $index 0}},{{end}}\"mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}}\"{{end}}]"
REDIS_DSN="[{{range $index, $service := service "redis"}}{{if ne $index 0}},{{end}}\"redis://{{.Address}}:{{.Port}}//\"{{end}}]"
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
        FEED_REF   = "france-intercity"
        FEED_URL   = "https://eu.ftp.opendatasoft.com/sncf/gtfs/export-intercites-gtfs-last.zip"
        SENTRY_DSN = "https://d86394991a184238865125d76e464d6d@sentry.snowfall.se/21"
      }
    }
  }
}
