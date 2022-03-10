job "planner" {
  datacenters = ["junction-dev-dc1"]
  type = "service"

  update {
    max_parallel = 1
    auto_revert = true
    auto_promote = true
    canary = 1
    healthy_deadline = "30s"
    progress_deadline = "2m"
  }

  group "grpc" {
    count = 1

    network {
      port "grpc" {}
    }

    service {
      name = "planner"
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

      resources {
        memory = 8192
      }

      vault {
        policies = ["planner-dev"]
      }

      config {
        image = "${DOCKER_IMAGE}"
        ports = ["grpc"]
        args = [
          "grpc",
        ]

        auth {
          username = "${NOMAD_REGISTRY_USERNAME}"
          password = "${NOMAD_REGISTRY_PASSWORD}"
          server_address = "${CI_REGISTRY}"
        }
      }

      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
{{ with secret "kv/dev/planner" }}
{{ if .Data.data.aws_access_key_id }}AWS_ACCESS_KEY_ID="{{ .Data.data.aws_access_key_id }}"{{ end }}
{{ if .Data.data.aws_secret_access_key }}AWS_SECRET_ACCESS_KEY="{{ .Data.data.aws_secret_access_key }}"{{ end }}
{{ end }}
EOH
      }

      artifact {
        source = "s3::https://junction-schedules-export.s3.eu-west-2.amazonaws.com/route_stops.bin"¨
        options {
          aws_access_key_id     = "${AWS_ACCESS_KEY_ID}"
          aws_access_key_secret = "${AWS_SECRET_ACCESS_KEY}"
        }
      }

      artifact {
        source = "s3::https://junction-schedules-export.s3.eu-west-2.amazonaws.com/routes.bin"
        options {
          aws_access_key_id     = "${AWS_ACCESS_KEY_ID}"
          aws_access_key_secret = "${AWS_SECRET_ACCESS_KEY}"
        }
      }

      artifact {
        source = "s3::https://junction-schedules-export.s3.eu-west-2.amazonaws.com/stops.bin"
        options {
          aws_access_key_id     = "${AWS_ACCESS_KEY_ID}"
          aws_access_key_secret = "${AWS_SECRET_ACCESS_KEY}"
        }
      }

      artifact {
        source = "s3::https://junction-schedules-export.s3.eu-west-2.amazonaws.com/transfers.bin"
        options {
          aws_access_key_id     = "${AWS_ACCESS_KEY_ID}"
          aws_access_key_secret = "${AWS_SECRET_ACCESS_KEY}"
        }
      }

      artifact {
        source = "s3::https://junction-schedules-export.s3.eu-west-2.amazonaws.com/schedule_stops.bin"
        options {
          aws_access_key_id     = "${AWS_ACCESS_KEY_ID}"
          aws_access_key_secret = "${AWS_SECRET_ACCESS_KEY}"
        }
      }

      artifact {
        source = "s3::https://junction-schedules-export.s3.eu-west-2.amazonaws.com/schedules.bin"
        options {
          aws_access_key_id     = "${AWS_ACCESS_KEY_ID}"
          aws_access_key_secret = "${AWS_SECRET_ACCESS_KEY}"
        }
      }

      env {
        GRPC_ADDRESS = "0.0.0.0"
        GRPC_PORT    = "${NOMAD_PORT_grpc}"
        PROTO_DIR    = "${NOMAD_TASK_DIR}"
        SENTRY_DSN   = "https://43837909119c4ce186975c300c4efe6e@sentry.snowfall.se/23"
      }
    }
  }
}
