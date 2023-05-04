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

variable "datacenter" {
  type = string
}

variable "environment" {
  type = string
}

variable "traefik_entrypoints" {
  type = string
}

variable "traefik_host_URL" {
  type = string
}

job "junction-http" {
  datacenters = ["${var.datacenter}"]
  type        = "service"

  update {
    max_parallel      = 1
    auto_revert       = true
    auto_promote      = true
    canary            = 1
    healthy_deadline  = "60s"
    progress_deadline = "2m"
  }

  group "http" {
    count = 1

    restart {
      attempts = 3
      delay    = "15s"
      interval = "10m"
      mode     = "delay"
    }

    network {
      mode = "bridge"
      port "http" {}
      port "prometheus" {}
    }

    scaling {
      enabled = false
      min     = 1
      max     = 20
    }

    service {
      name = "docs-junction-${var.environment}"
      port = "http"
      tags = [
        "http",
        "traefik.enable=true",
        "traefik.http.routers.docs-junction-${var.environment}.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.docs-junction-${var.environment}.rule=Host(`${var.traefik_host_URL}`)",
        "traefik.http.routers.docs-junction-${var.environment}.middlewares=docs-junction-auth",
        "traefik.http.middlewares.docs-junction-auth.basicauth.users=snowfall:$apr1$nVeL//e6$BP5DcRDvCLbuXfWca.jzc." // snowfall / N6z5fu&dTvp7j4rgK4V1uPrG
      ]
    }

    task "http" {
      driver = "docker"

      config {
        image = var.docker_image
        ports = ["http"]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {
        NGINX_PORT = "${NOMAD_PORT_http}"
      }
    }
  }
}
