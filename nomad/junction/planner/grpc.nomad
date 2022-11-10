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

variable "environment" {
  type = string
}

variable "datacenter" {
  type = string
}

job "planner-grpc" {
  datacenters = ["${var.datacenter}"]
  type        = "service"
  priority    = 75
  update {
    max_parallel      = 1
    auto_revert       = true
    auto_promote      = true
    healthy_deadline  = "10m"
    progress_deadline = "15m"
    canary            = 1
  }

  group "grpc" {
    count = 1

    restart {
      attempts = 3
      delay    = "15s"
      interval = "10m"
      mode     = "delay"
    }

    network {
      mode = "bridge"
      port "grpc" {}
    }

    service {
      name = "planner-${var.environment}"
      port = "grpc"
      tags = ["grpc"]

      connect {
        sidecar_service {}
      }

      check {
        type     = "grpc"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "grpc" {
      driver = "docker"

      resources {
        memory = 10 * 1024
      }

      config {

        image = var.docker_image
        ports = ["grpc"]
        args = [
          "grpc",
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      artifact {
        source = "s3::https://s3-eu-west-2.amazonaws.com/junction-schedules-export/route_stops.bin"
        options {
          aws_access_key_id     = "AKIA6JO5TGEWEV7G2IHA"
          aws_access_key_secret = "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"
        }
      }

      artifact {
        source = "s3::https://s3-eu-west-2.amazonaws.com/junction-schedules-export/routes.bin"
        options {
          aws_access_key_id     = "AKIA6JO5TGEWEV7G2IHA"
          aws_access_key_secret = "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"
        }
      }

      artifact {
        source = "s3::https://s3-eu-west-2.amazonaws.com/junction-schedules-export/stops.bin"
        options {
          aws_access_key_id     = "AKIA6JO5TGEWEV7G2IHA"
          aws_access_key_secret = "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"
        }
      }

      artifact {
        source = "s3::https://s3-eu-west-2.amazonaws.com/junction-schedules-export/transfers.bin"
        options {
          aws_access_key_id     = "AKIA6JO5TGEWEV7G2IHA"
          aws_access_key_secret = "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"
        }
      }

      artifact {
        source = "s3::https://s3-eu-west-2.amazonaws.com/junction-schedules-export/schedule_stops.bin"
        options {
          aws_access_key_id     = "AKIA6JO5TGEWEV7G2IHA"
          aws_access_key_secret = "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"
        }
      }

      artifact {
        source = "s3::https://s3-eu-west-2.amazonaws.com/junction-schedules-export/schedules.bin"
        options {
          aws_access_key_id     = "AKIA6JO5TGEWEV7G2IHA"
          aws_access_key_secret = "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"
        }
      }

      env {
        ENV_NAME     = "${var.environment}"
        GRPC_ADDRESS = "0.0.0.0"
        GRPC_PORT    = "${NOMAD_PORT_grpc}"
        PROTO_DIR    = "${NOMAD_TASK_DIR}"
        SENTRY_DSN   = "https://43837909119c4ce186975c300c4efe6e@sentry.snowfall.se/23"
      }
    }
  }
}
