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

job "planner-grpc" {
  datacenters = ["${var.datacenter}"]
  type        = "service"
  priority    = 75
  update {
    max_parallel      = 1
    auto_revert       = true
    auto_promote      = true
    healthy_deadline  = "25m"
    progress_deadline = "30m"
    canary            = 1
  }

  group "grpc" {
    count = "${var.count}"

    restart {
      attempts = 3
      delay    = "15s"
      interval = "10m"
      mode     = "delay"
    }

    network {
      mode = "bridge"
      port "grpc" {}
      port "prometheus" {}
    }

    scaling {
      enabled = false
      min     = 1
      max     = 20
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

    service {
      name = "planner-${var.environment}"
      port = "prometheus"
      tags = ["metrics"]

      check {
        type     = "http"
        path     = "/metrics"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "grpc" {
      driver = "docker"

      resources {
        memory     = 75 * 1024
        memory_max = 129 * 1024
      }

      config {

        image = var.docker_image
        ports = ["grpc"]
        args = [
          "serve",
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
        volumes = [
          "/planner-efs/${var.environment}:/local/data"
        ]
      }



      env {
        ENV_NAME        = "${var.environment}"
        GRPC_ADDRESS    = "0.0.0.0"
        GRPC_PORT       = "${NOMAD_PORT_grpc}"
        PROTO_DIR       = "/local/data"
        PROMETHEUS_PORT = "${NOMAD_PORT_prometheus}"
        SENTRY_DSN      = "https://43837909119c4ce186975c300c4efe6e@sentry.snowfall.se/23"
      }
    }
  }
}
