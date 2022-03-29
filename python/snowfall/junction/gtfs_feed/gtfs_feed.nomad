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
AMQP_DSN={{range $index, $service := service "amqp"}}amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}// {{end}}
MONGO_DSN={{range $index, $service := service "mongodb"}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}
REDIS_DSN={{range $index, $service := service "redis"}}redis://{{.Address}}:{{.Port}}// {{end}}
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = var.docker_image
        args = [
          "import",
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {
        ENV_NAME   = "${NOMAD_NAMESPACE}"
        FEED_REF   = "france-intercity"
        FEED_URL   = "https://eu.ftp.opendatasoft.com/sncf/gtfs/export-intercites-gtfs-last.zip"
        SENTRY_DSN = "https://d86394991a184238865125d76e464d6d@sentry.snowfall.se/21"
      }
    }
  }
}
