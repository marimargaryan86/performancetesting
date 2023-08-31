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

variable "search_timeout" {
  type = string
}

job "gateway-consume" {
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

  group "consume" {
    count = "${var.count}"

    restart {
      attempts = 3
      delay    = "15s"
      interval = "10m"
      mode     = "delay"
    }

    network {
      mode = "bridge"
      port "prometheus" {}
    }

    scaling {
      enabled = false
      min     = 1
      max     = 20
    }

    service {
      name = "${JOB}-${var.environment}"
      port = "prometheus"
      tags = ["metrics"]

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
            upstreams {
              local_bind_port  = 8040
              destination_name = "ba-ndc-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8050
              destination_name = "direct-ferries-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8060
              destination_name = "distribusion-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8070
              destination_name = "duffel-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8080
              destination_name = "benerail-${var.environment}"
            }
          }
        }
      }

      check {
        type     = "http"
        path     = "/"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "consume" {
      driver = "docker"

      template {
        data        = <<EOH
AMQP_DSN={{range $index, $service := service "amqp-${var.environment}"}}amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}// {{end}}
REDIS_DSN={{range $index, $service := service "redis-${var.environment}"}}redis://{{.Address}}:{{.Port}}// {{end}}
PROVIDERS="{
{{- ""}}\"4b7d12db-7735-4c67-9645-5fc82f7c4fe8\":\"{{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_ask2go-${var.environment}"))}}\",
{{- ""}}\"f9ce75d1-2025-4ab5-b5d7-69e4c14c053e\":\"{{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_mock-${var.environment}"))}}\",
{{- ""}}\"a5547dae-9c65-4746-8637-d0601865508e\":\"{{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_save-a-train-${var.environment}"))}}\",
{{- ""}}\"f1f884bf-0be6-4ce2-8414-296a775a508d\":\"{{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_ba-ndc-${var.environment}"))}}\",
{{- ""}}\"92ada881-f31c-471e-a8b0-01ed48a181d5\":\"{{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_direct-ferries-${var.environment}"))}}\",
{{- ""}}\"30bfba87-7077-4d96-beed-c5769cdc99c7\":\"{{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_distribusion-${var.environment}"))}}\",
{{- ""}}\"5d18e8e1-48e3-4b7c-82b9-62bd97a92f91\":\"{{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_duffel-${var.environment}"))}}\",
{{- ""}}\"caefde65-c15c-4b60-b8d9-27638b50b08f\":\"{{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_benerail-${var.environment}"))}}\"
{{- ""}}}"
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = var.docker_image
        ports = ["prometheus"]
        args = [
          "consume",
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {
        ENV_NAME        = "${var.environment}"
        SENTRY_DSN      = "https://a7dc859d8f87421293496a948693c9c5@sentry.snowfall.se/128"
        PROMETHEUS_PORT = "${NOMAD_PORT_prometheus}"
        SEARCH_TIMEOUT  = var.search_timeout
      }
    }
  }
}
