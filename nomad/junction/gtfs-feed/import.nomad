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
    {ref = "belgium", url = "https://gtfs.irail.be/nmbs/gtfs/latest.zip?archive=false"},
    {ref = "france-intercity", url = "https://eu.ftp.opendatasoft.com/sncf/gtfs/export-intercites-gtfs-last.zip?archive=false"},
    {ref = "france-ter", url = "https://eu.ftp.opendatasoft.com/sncf/gtfs/export-ter-gtfs-last.zip?archive=false"},
    {ref = "france-transilien", url = "https://eu.ftp.opendatasoft.com/sncf/gtfs/gtfs-nouveau-format.zip?archive=false"},
    {ref = "france-voyages", url = "https://eu.ftp.opendatasoft.com/sncf/gtfs/export_gtfs_voyages.zip?archive=false"},
    {ref = "luxembourg", url = "http://openov.lu/data/gtfs/gtfs-openov-lu.zip?archive=false"},
    {ref = "netherlands", url = "http://gtfs.ovapi.nl/gtfs-nl.zip?archive=false"},
  ]
}

job "gtfs-feed-import" {
  datacenters = ["junction-dev-dc1"]
  type        = "batch"

  periodic {
    cron             = "@weekly"
    prohibit_overlap = true
  }

  group "ssim" {
    count = 1

    task "download" {
      lifecycle {
        hook = "prestart"
      }

      driver = "docker"

      vault {
        policies = ["gtfs-feed-dev"]
      }

      template {
        data        = <<EOH
{{ with secret "kv/dev/gtfs-feed" }}
AWS_ACCESS_KEY_ID={{ .Data.data.aws_access_key_id }}
AWS_SECRET_ACCESS_KEY={{ .Data.data.aws_secret_access_key }}
{{ end }}
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = "amazon/aws-cli"
        args = [
          "s3",
          "mv",
          "s3://junction-gtfs-feeds",
          "${NOMAD_ALLOC_DIR}/",
          "--recursive"
        ]
      }

      env {
        AWS_DEFAULT_REGION = "eu-west-2"
      }
    }

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
        FEEDS_DIR  = "${NOMAD_ALLOC_DIR}"
        SENTRY_DSN = "https://d86394991a184238865125d76e464d6d@sentry.snowfall.se/21"
      }
    }
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

        artifact {
          source = group.value.url
          destination = "${NOMAD_TASK_DIR}/${group.value.ref}.zip"
          mode = "file"
        }

        env {
          ENV_NAME   = "${NOMAD_NAMESPACE}"
          FEEDS_DIR  = "${NOMAD_TASK_DIR}"
          SENTRY_DSN = "https://d86394991a184238865125d76e464d6d@sentry.snowfall.se/21"
        }
      }
    }
  }
}
