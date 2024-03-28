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

variable "j_one_api_base_url" {
  type = string
}

job "junction-rocket-api-http" {
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
    }

    scaling {
      enabled = false
      min     = 1
      max     = 20
    }

    service {
      name = "rocket-api-${var.environment}"
      port = "http"
      tags = [
        "traefik.enable=true",
        "traefik.consulcatalog.connect=true",
        "traefik.http.routers.rocket-api-${var.environment}.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.rocket-api-${var.environment}.rule=Host(`${var.traefik_host_URL}`)",
      ]

      connect {
        sidecar_service {
          proxy {
            upstreams {
              local_bind_port  = 8010
              destination_name = "authentication-${var.environment}"
            }

            upstreams {
              local_bind_port  = 8020
              destination_name = "searches-${var.environment}"
            }
          }
        }
      }

      check {
        type     = "http"
        path     = "/health"
        interval = "30s"
        timeout  = "4s"
      }
    }

    task "http" {
      driver = "docker"

      vault {
        policies = ["rocket-api-${var.environment}"]
      }

      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
AUTHENTICATION_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_authentication-${var.environment}"))}}
SEARCHES_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_searches-${var.environment}"))}}
RESELLER_J1_CREDENTIALS_MAPPING={{keyOrDefault "${var.environment}/rocket-api/reseller-j1-credentials-mapping" "{}" | toJSON }}
{{ with secret "kv/data/${var.environment}/rocket-api" }}
J_ONE_API_KEY={{ .Data.data.j_one_api_key }}
{{ end }}
EOH
      }

      config {
        image = var.docker_image
        ports = ["http"]
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
        ENV_NAME              = "${var.environment}"
        FORWARDED_ALLOWED_IPS = "0.0.0.0"
        HTTP_ADDRESS          = "0.0.0.0"
        HTTP_PORT             = "${NOMAD_PORT_http}"
        SENTRY_DSN            = "https://303cafc116e642efe7c538795b0c2e7a@sentry.snowfall.se/238"
        J_ONE_API_BASE_URL    = "${var.j_one_api_base_url}"
      }
    }
  }
}

