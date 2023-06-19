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

job "gateway-serve" {
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

  group "serve" {
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
      name = "gateway-${var.environment}"
      port = "grpc"
      tags = ["grpc"]

      connect {
        sidecar_service {
          proxy {
            upstreams {
              local_bind_port  = 8010
              destination_name = "mock-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8020
              destination_name = "ask2go-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8030
              destination_name = "save-a-train-${var.environment}"
            }
          }
        }
      }

      check {
        type     = "grpc"
        interval = "30s"
        timeout  = "4s"
      }
    }
    service {
      name = "gateway-${var.environment}"
      port = "prometheus"
      tags = ["metrics"]

      check {
        type     = "http"
        path     = "/"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "serve" {
      driver = "docker"

      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
AMQP_DSN={{range $index, $service := service "amqp-${var.environment}"}}amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}// {{end}}
PROVIDERS={{- "{\"" }}f9ce75d1-2025-4ab5-b5d7-69e4c14c053e{{- "\":\"" }}{{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_mock-${var.environment}"))}}{{- "\",\"" }}4b7d12db-7735-4c67-9645-5fc82f7c4fe8{{- "\":\"" }}{{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_ask2go-${var.environment}"))}}{{- "\",\"" }}a5547dae-9c65-4746-8637-d0601865508e{{- "\":\"" }}{{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_save-a-train-${var.environment}{{- "\"" }}))}}{{- "\"}" }}
REDIS_DSN={{range $index, $service := service "redis-${var.environment}"}}redis://{{.Address}}:{{.Port}}// {{end}}
EOH
      }

      config {
        image = var.docker_image
        ports = ["grpc", "prometheus"]
        args = [
          "serve",
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {
        ENV_NAME        = "${var.environment}"
        GRPC_ADDRESS    = "0.0.0.0"
        GRPC_PORT       = "${NOMAD_PORT_grpc}"
        SENTRY_DSN      = "https://a7dc859d8f87421293496a948693c9c5@sentry.snowfall.se/128"
        PROMETHEUS_PORT = "${NOMAD_PORT_prometheus}"
      }
    }
  }
}
