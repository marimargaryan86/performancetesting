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

variable "count" {
  type = number
}

variable "google_flights_emissions_address" {
  type = string
}

job "junction-plus-external-dependencies-grpc" {
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

  group "grpc" {
    count = var.count

    restart {
      attempts = 3
      delay    = "15s"
      interval = "10m"
      mode     = "delay"
    }

    scaling {
      enabled = false
      min     = 1
      max     = 20
    }

    network {
      mode = "bridge"
      port "grpc" {}
      port "prometheus" {}
    }

    service {
      name = "external-dependencies-grpc-${var.environment}"
      port = "grpc"
      tags = ["grpc"]

      connect {
        sidecar_service {}
      }

      check {
        type     = "grpc"
        interval = "30s"
        timeout  = "4s"
      }
    }

    service {
      name = "external-dependencies-prometheus-${var.environment}"
      port = "prometheus"
      tags = ["metrics"]

      check {
        type     = "http"
        path     = "/"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "grpc" {
      driver = "docker"

      vault {
        policies = ["external-dependencies-${var.environment}"]
      }

      template {
        data        = <<EOH
{{ with secret "kv/data/${var.environment}/external-dependencies" }}
GOOGLE_FLIGHTS_EMISSIONS_APP_KEY={{ .Data.data.google_flights_emissions_app_key }}
{{ end }}
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = var.docker_image
        ports = ["grpc", "prometheus"]
        args  = ["grpc"]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {
        ENV_NAME                         = var.environment
        GRPC_ADDRESS                     = "0.0.0.0"
        GRPC_PORT                        = NOMAD_PORT_grpc
        SENTRY_DSN                       = "https://202eca9b6fe37ea1e154b827362ccfa9@sentry.snowfall.se/205"
        PROMETHEUS_PORT                  = NOMAD_PORT_prometheus
        GOOGLE_FLIGHTS_EMISSIONS_ADDRESS = var.google_flights_emissions_address
      }
    }
  }
}
