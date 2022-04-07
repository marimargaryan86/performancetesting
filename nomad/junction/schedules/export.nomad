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

job "schedules-export" {
  datacenters = ["junction-dev-dc1"]
  type        = "batch"

  periodic {
    cron             = "@hourly"
    prohibit_overlap = true
  }

  group "export" {
    count = 1

    ephemeral_disk {
      size = 10000
    }

    task "export" {
      driver = "docker"

      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
MONGO_DSN={{range $index, $service := service "mongodb"}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}
REDIS_DSN={{range $index, $service := service "redis"}}redis://{{.Address}}:{{.Port}}// {{end}}
EOH
      }

      config {
        image = var.docker_image
        args = [
          "export",
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {
        ENV_NAME     = "${NOMAD_NAMESPACE}"
        OUTPUT_PATH  = "${NOMAD_ALLOC_DIR}"
        SENTRY_DSN   = "https://8d94d1ca059f4dc9b4e1e91dfd3d7151@sentry.snowfall.se/25"
      }
    }
  }
}
