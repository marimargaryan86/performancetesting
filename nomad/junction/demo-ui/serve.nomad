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

job "junction-demo-ui-serve" {
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

  group "serve" {
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
      name = "${JOB}-${var.environment}"
      port = "http"
      tags = [
        "http",
        "traefik.enable=true",
        "traefik.consulcatalog.connect=true",
        "traefik.http.routers.demo-ui-${var.environment}.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.demo-ui-${var.environment}.middlewares=dogfood-auth",
        "traefik.http.routers.demo-ui-${var.environment}.rule=Host(`${var.traefik_host_URL}`)",
        "traefik.http.middlewares.demo-auth.basicauth.users=snowfall:$apr1$nVeL//e6$BP5DcRDvCLbuXfWca.jzc." // snowfall / N6z5fu&dTvp7j4rgK4V1uPrG
      ]

      connect {
        sidecar_service {
          proxy {
            upstreams {
              local_bind_port  = 7000
              destination_name = "junction-gateway-serve-${var.environment}"
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
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "serve" {
      driver = "docker"

      template {
        data        = <<EOH
GATEWAY_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_junction-gateway-serve-${var.environment}"))}}
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = var.docker_image
        ports = ["http", "prometheus"]
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
        ENV_NAME              = "${var.environment}"
        FORWARDED_ALLOWED_IPS = "0.0.0.0"
        HTTP_ADDRESS          = "0.0.0.0"
        HTTP_PORT             = "${NOMAD_PORT_http}"
        SENTRY_DSN            = "https://bbd902506c4bdcc37c30cea750cd61eb@sentry.snowfall.se/209"
        PROMETHEUS_PORT       = "${NOMAD_PORT_prometheus}"
      }
    }
  }
}
