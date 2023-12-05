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

variable "allure_api_URL" {
  type = string
}

job "vendor-allure-ui-http" {
  datacenters = ["${var.datacenter}"]
  type        = "service"

  update {
    max_parallel      = 1
    auto_revert       = true
    auto_promote      = true
    canary            = 1
    healthy_deadline  = "2m"
    progress_deadline = "4m"
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
      port "http" {
        to = 5252
      }

    }

    service {
      name = "allure-ui-${var.environment}"
      port = "http"
      tags = [
        "http",
        "traefik.enable=true",
        "traefik.http.routers.allure-ui-${var.environment}.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.allure-ui-${var.environment}.rule=Host(`${var.traefik_host_URL}`)",
      ]

      check {
        type     = "http"
        path     = "/"
        interval = "30s"
        timeout  = "4s"
      }
    }

    task "http" {
      driver = "docker"

      config {
        image = "frankescobar/allure-docker-service-ui:latest"
        ports = ["http"]
      }

      env {
        ENV_NAME                       = "${NOMAD_NAMESPACE}"
        CHECK_RESULTS_EVERY_SECONDS    = "NONE"
        KEEP_HISTORY                   = "1"
        KEEP_HISTORY_LATEST            = "25"
        HTTP_ADDRESS                   = "0.0.0.0"
        ALLURE_DOCKER_SERVICE_API_PORT = "${NOMAD_PORT_http}"
        ALLURE_DOCKER_PUBLIC_API_URL   = "${var.allure_api_URL}"
      }
    }
  }
}
