job "gtfs-feed" {
  datacenters = ["junction-dev-dc1"]
  type        = "batch"

  periodic {
    cron             = "@daily"
    prohibit_overlap = true
  }

  group "belgium" {
    count = 1

    ephemeral_disk {
      size = 1000
    }

    task "belgium" {
      driver = "docker"

      template {
          data        = <<EOH
AMQP_DSN="[{{range $index, $service := service "amqp"}}{{if ne $index 0}},{{end}}\"amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}//\"{{end}}]"
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
        FEED_URL   = "https://gtfs.irail.be/nmbs/gtfs/latest.zip"
        SENTRY_DSN = "https://d86394991a184238865125d76e464d6d@sentry.snowfall.se/21"
      }
    }
  }

  group "denmark" {
    count = 1

    ephemeral_disk {
      size = 1000
    }

    task "denmark" {
      driver = "docker"

      template {
        data        = <<EOH
AMQP_DSN="[{{range $index, $service := service "amqp"}}{{if ne $index 0}},{{end}}\"amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}//\"{{end}}]"
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
        FEED_URL   = "http://www.rejseplanen.info/labs/GTFS.zip"
        SENTRY_DSN = "https://d86394991a184238865125d76e464d6d@sentry.snowfall.se/21"
      }
    }
  }

  group "netherlands" {
    count = 1

    ephemeral_disk {
      size = 1000
    }

    task "netherlands" {
      driver = "docker"

      template {
        data        = <<EOH
AMQP_DSN="[{{range $index, $service := service "amqp"}}{{if ne $index 0}},{{end}}\"amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}//\"{{end}}]"
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
        FEED_URL   = "http://gtfs.ovapi.nl/gtfs-nl.zip"
        SENTRY_DSN = "https://d86394991a184238865125d76e464d6d@sentry.snowfall.se/21"
      }
    }
  }

  group "sweden" {
    count = 1

    ephemeral_disk {
      size = 1000
    }

    task "sweden" {
      driver = "docker"

      template {
        data        = <<EOH
AMQP_DSN="[{{range $index, $service := service "amqp"}}{{if ne $index 0}},{{end}}\"amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}//\"{{end}}]"
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
        FEED_URL   = "https://transitfeeds.com/p/trafiklab/50/latest/download"
        SENTRY_DSN = "https://d86394991a184238865125d76e464d6d@sentry.snowfall.se/21"
      }
    }
  }
}
