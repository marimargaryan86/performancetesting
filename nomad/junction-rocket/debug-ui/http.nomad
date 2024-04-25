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

job "junction-rocket-debug-ui-http" {
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
      port "prometheus" {}
    }

    scaling {
      enabled = false
      min     = 1
      max     = 20
    }

    service {
      name = "${JOB}-${var.environment}"
      port = "http"
      tags = [
        "http",
        "traefik.enable=true",
        "traefik.consulcatalog.connect=true",
        "traefik.http.routers.debug-ui-${var.environment}.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.debug-ui-${var.environment}.middlewares=debug-auth",
        "traefik.http.routers.debug-ui-${var.environment}.rule=Host(`${var.traefik_host_URL}`)",
        "traefik.http.middlewares.debug-auth.basicauth.users=snowfall:$apr1$nVeL//e6$BP5DcRDvCLbuXfWca.jzc." // snowfall / N6z5fu&dTvp7j4rgK4V1uPrG
      ]

      connect {
        sidecar_service {
          proxy {
            upstreams {
              local_bind_port  = 8010
              destination_name = "places-${var.environment}"
            }

            upstreams {
              local_bind_port  = 8020
              destination_name = "planner-${var.environment}"
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

    service {
      name = "${JOB}-${var.environment}"
      port = "prometheus"
      tags = ["metrics"]

      check {
        type     = "http"
        path     = "/"
        interval = "30s"
        timeout  = "4s"
      }
    }

    task "http" {
      driver = "docker"

      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
PLANNER_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_planner-${var.environment}"))}}
PLACES_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_places-${var.environment}"))}}
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
        ENV_NAME              = "${var.environment}"
        FORWARDED_ALLOWED_IPS = "0.0.0.0"
        HTTP_ADDRESS          = "0.0.0.0"
        HTTP_PORT             = "${NOMAD_PORT_http}"
        PROMETHEUS_PORT       = "${NOMAD_PORT_prometheus}"
        SENTRY_DSN            = "https://4b9bf0d9fb599493773f932ebe2469cd@sentry.snowfall.se/266"
      }
    }
  }
}

