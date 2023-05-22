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

variable "traefik_entrypoints" {
  type = string
}

variable "traefik_host_URL" {
  type = string
}

variable "count" {
  type = number
}

variable "data_api_host" {
  type = string
}

job "data-api-http" {
  datacenters = ["${var.datacenter}"]
  type        = "service"

  update {
    max_parallel      = 1
    auto_revert       = true
    auto_promote      = true
    canary            = 1
    healthy_deadline  = "1m"
    progress_deadline = "2m"
  }

  group "http" {
    count = "${var.count}"

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
      name = "data-api-${var.environment}"
      port = "http"
      tags = [
        "http",
        "traefik.enable=true",
        "traefik.consulcatalog.connect=true",
        "traefik.http.routers.data-api-${var.environment}.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.data-api-${var.environment}.rule=Host(`${var.traefik_host_URL}`)",
      ]

      connect {
        sidecar_service {
          proxy {
            upstreams {
              local_bind_port  = 8020
              destination_name = "geodata-${var.environment}"
            }
          }
        }
      }

      check {
        type     = "http"
        path     = "/health"
        interval = "10s"
        timeout  = "2s"
      }
    }

    service {
      name = "data-api-${var.environment}"
      port = "prometheus"
      tags = ["metrics"]

      check {
        type     = "http"
        path     = "/"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "http" {
      driver = "docker"

      resources {
        memory = 600
      }

      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
GEODATA_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_geodata-${var.environment}"))}}
EOH
      }

      config {
        image = var.docker_image
        ports = ["http", "prometheus"]
        args = [
          "http",
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {
        ENV_NAME                        = "${var.environment}"
        FORWARDED_ALLOWED_IPS           = "0.0.0.0"
        HTTP_ADDRESS                    = "0.0.0.0"
        HTTP_PORT                       = "${NOMAD_PORT_http}"
        SENTRY_DSN                      = "https://07b6d5a555bc4b7d88c6b552488016ae@sentry.snowfall.se/70"
        PROMETHEUS_PORT                 = "${NOMAD_PORT_prometheus}"
        VALIDATE_RESPONSES_AGAINST_SPEC = false
        DATA_API_HOST                   = "${var.data_api_host}"
      }
    }
  }
}
