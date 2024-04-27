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

variable "base_url_URL" {
  type = string
}

variable "static_places_file" {
  type = string
}

variable "downstream_timeout" {
  type = string
}

job "junction-go-dogfood-ui-http" {
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
      name = "dogfood-ui-${var.environment}"
      port = "http"
      tags = [
        "http",
        "traefik.enable=true",
        "traefik.consulcatalog.connect=true",
        "traefik.http.routers.dogfood-ui-${var.environment}.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.dogfood-ui-${var.environment}.middlewares=dogfood-auth",
        "traefik.http.routers.dogfood-ui-${var.environment}.rule=Host(`${var.traefik_host_URL}`)",
        "traefik.http.middlewares.dogfood-auth.basicauth.users=snowfall:$apr1$nVeL//e6$BP5DcRDvCLbuXfWca.jzc." // snowfall / N6z5fu&dTvp7j4rgK4V1uPrG
      ]

      connect {
        sidecar_service {}
      }

      check {
        type     = "http"
        path     = "/health"
        interval = "30s"
        timeout  = "4s"
      }
    }

    service {
      name = "dogfood-ui-${var.environment}"
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

      vault {
        policies = ["dogfood-ui-${var.environment}"]
      }
      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
{{ with secret "kv/data/${var.environment}/dogfood-ui" }}
AUTH_TOKEN={{ .Data.data.auth_token }}
{{ end }}
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
        BASE_URL              = "${var.base_url_URL}"
        STATIC_PLACES_FILE    = "${var.static_places_file}"
        SENTRY_DSN            = "https://063e03b4d8fd4fa7b13e0729950f3cee@sentry.snowfall.se/52"
        PROMETHEUS_PORT       = "${NOMAD_PORT_prometheus}"
        DOWNSTREAM_TIMEOUT    = "${var.downstream_timeout}"
      }
    }
  }
}
