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

locals {
  feeds = [
    {ref = "belgium", url = "https://gtfs.irail.be/nmbs/gtfs/latest.zip"},
    {ref = "france-intercity", url = "https://eu.ftp.opendatasoft.com/sncf/gtfs/export-intercites-gtfs-last.zip"},
    {ref = "france-ter", url = "https://eu.ftp.opendatasoft.com/sncf/gtfs/export-ter-gtfs-last.zip"},
    {ref = "france-transilien", url = "https://eu.ftp.opendatasoft.com/sncf/gtfs/gtfs-nouveau-format.zip"},
    {ref = "france-voyages", url = "https://eu.ftp.opendatasoft.com/sncf/gtfs/export_gtfs_voyages.zip"},
    {ref = "luxembourg", url = "http://openov.lu/data/gtfs/gtfs-openov-lu.zip"},
    {ref = "netherlands", url = "http://gtfs.ovapi.nl/gtfs-nl.zip"},
  ]
}

job "gtfs-feed-import" {
  datacenters = ["junction-dev-dc1"]
  type        = "batch"

  periodic {
    cron             = "@weekly"
    prohibit_overlap = true
  }

  dynamic "group" {
    for_each = local.feeds
    labels = ["${group.value.ref}"]

    content {
      count = 1

      task "import" {
        driver = "docker"

        template {
          data        = <<EOH
  AMQP_DSN={{range $index, $service := service "amqp"}}amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}// {{end}}
  GEODATA_ADDRESS={{range $index, $service := service (printf "grpc.geodata-%s" (env "NOMAD_NAMESPACE"))}}{{.Address}}:{{.Port}} {{end}}
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
          FEED_REF   = group.value.ref
          FEED_URL   = group.value.url
          SENTRY_DSN = "https://d86394991a184238865125d76e464d6d@sentry.snowfall.se/21"
        }
      }
    }
  }
}
