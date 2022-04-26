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

job "ssim-convert-convert" {
  datacenters = ["junction-dev-dc1"]
  type = "batch"

  periodic {
    cron             = "@weekly"
    prohibit_overlap = true
  }

  group "convert" {
    count = 1

    task "convert" {
      driver = "docker"

      config {
        image = var.docker_image
        args = [
          "convert",
          "${NOMAD_TASK_DIR}/SIMSFL.DAT",
          "${NOMAD_TASK_DIR}/feeds"
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      artifact {
        source = "s3::https://s3-eu-west-2.amazonaws.com/junction-ssim-data/SIMSFL.DAT"
        options {
          aws_access_key_id     = "AKIA6JO5TGEWLRCUW75V"
          aws_access_key_secret = "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"
        }
      }

      env {
        ENV_NAME     = "${NOMAD_NAMESPACE}"
        SENTRY_DSN   = "https://43837909119c4ce186975c300c4efe6e@sentry.snowfall.se/23"
      }
    }
  }
}
