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

  group "grpc" {
    count = 1

    network {
      port "grpc" {}
    }

    service {
      name = "schedules"
      port = "grpc"
      tags = ["grpc"]

      check {
        type     = "grpc"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "grpc" {
      driver = "docker"

      template {
        data        = <<EOH
MONGO_DSN="[{{range $index, $service := service "mongodb"}}{{if ne $index 0}},{{end}}\"mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}}\"{{end}}]"
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = "${DOCKER_IMAGE}"
        ports = ["grpc"]
        args = [
          "grpc",
        ]

        auth {
          username       = "${NOMAD_REGISTRY_USERNAME}"
          password       = "${NOMAD_REGISTRY_PASSWORD}"
          server_address = "${CI_REGISTRY}"
        }
      }

      env {
        ENV_NAME     = "junction.dev"
        GRPC_ADDRESS = "0.0.0.0"
        GRPC_PORT    = "${NOMAD_PORT_grpc}"
        SENTRY_DSN   = "https://8d94d1ca059f4dc9b4e1e91dfd3d7151@sentry.snowfall.se/25"
      }
    }
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
AMQP_DSN="[{{range $index, $service := service "amqp"}}{{if ne $index 0}},{{end}}\"amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}//\"{{end}}]"
MONGO_DSN="[{{range $index, $service := service "mongodb"}}{{if ne $index 0}},{{end}}\"mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}}\"{{end}}]"
{{ with secret "kv/dev/schedules" }}
{{ if .Data.data.aws_access_key_id }}AWS_ACCESS_KEY_ID="{{ .Data.data.aws_access_key_id }}"{{ end }}
{{ if .Data.data.aws_secret_access_key }}AWS_SECRET_ACCESS_KEY="{{ .Data.data.aws_secret_access_key }}"{{ end }}
{{ end }}
EOH
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
        ENV_NAME     = "junction.dev"
        SENTRY_DSN   = "https://8d94d1ca059f4dc9b4e1e91dfd3d7151@sentry.snowfall.se/25"
        UPLOAD_TO_S3 = "true"
      }
    }
  }
}
