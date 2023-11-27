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

job "allure-api-http" {
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
        to = 5050
      }

    }

    service {
      name = "allure-api-${var.environment}"
      port = "http"
      tags = [
        "http",
        "traefik.enable=true",
        "traefik.http.routers.allure-api-${var.environment}.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.allure-api-${var.environment}.rule=Host(`${var.traefik_host_URL}`)",
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

      resources {
        memory = 1024
      }

      vault {
        policies = ["allure-${var.environment}"]
      }
      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
{{ with secret "kv/data/${var.environment}/allure" }}
SECURITY_USER={{ .Data.data.security_user }}
SECURITY_PASS={{ .Data.data.security_pass }}
{{ end }}
EOH
      }
      config {
        image = "frankescobar/allure-docker-service:latest"
        ports = ["http"]

        volumes = [
          "/allure-efs/projects:/app/projects"
        ]

      }

      env {
        ENV_NAME                       = "${NOMAD_NAMESPACE}"
        CHECK_RESULTS_EVERY_SECONDS    = "NONE"
        KEEP_HISTORY                   = "1"
        KEEP_HISTORY_LATEST            = "25"
        HTTP_ADDRESS                   = "0.0.0.0"
        SECURITY_ENABLED               = "1"
        ALLURE_DOCKER_SERVICE_API_PORT = "${NOMAD_PORT_http}"
        ACCESS_TOKEN_EXPIRES_IN_MINS   = "60"
      }
    }
  }
}

