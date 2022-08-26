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

job "pay-ui" {
  datacenters = ["junction-dev-dc1"]
  type        = "service"

  update {
    max_parallel      = 1
    auto_revert       = true
    auto_promote      = true
    canary            = 1
    healthy_deadline  = "30s"
    progress_deadline = "1m"
  }

  group "http" {
    count = 1

    service {
      name = "pay-ui-${NOMAD_NAMESPACE}"
      port = "http"
      tags = [
        "traefik.enable=true",
        "traefik.http.routers.junction-pay.entrypoints=websecure",
        "traefik.http.routers.junction-pay.rule=Host(`pay.junction.dev`)",
      ]

      check {
        type     = "http"
        path     = "/"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "http" {
      driver = "docker"

      config {
        image = var.docker_image

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }
    }
  }
}
