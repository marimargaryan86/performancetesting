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

job "schedules-import" {
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

      vault {
        policies = ["schedules-dev"]
      }

      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
AMQP_DSN={{range $index, $service := service "amqp"}}amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}// {{end}}
MONGO_DSN={{range $index, $service := service "mongodb"}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}
{{ with secret "kv/dev/schedules" }}
AWS_ACCESS_KEY_ID={{ .Data.data.aws_access_key_id }}
AWS_SECRET_ACCESS_KEY={{ .Data.data.aws_secret_access_key }}
{{ end }}
EOH
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
        ENV_NAME     = "${NOMAD_NAMESPACE}"
        SENTRY_DSN   = "https://8d94d1ca059f4dc9b4e1e91dfd3d7151@sentry.snowfall.se/25"
        UPLOAD_TO_S3 = "true"
      }
    }
  }
}
