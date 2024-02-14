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

variable "ory_base_url" {
  type = string
}

job "junction-hub-hub-web-http" {
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
      name = "hub-web-${var.environment}"
      port = "http"
      tags = [
        "traefik.enable=true",
        "traefik.consulcatalog.connect=true",
        "traefik.http.middlewares.hub-web-${var.environment}-headers.headers.browserXssFilter=true",
        "traefik.http.middlewares.hub-web-${var.environment}-headers.headers.contentsecuritypolicy=default-src 'self' https://fonts.googleapis.com; object-src 'none'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; script-src 'self' 'unsafe-eval' 'unsafe-inline' blob: https://sentry.snowfall.se https://js.stripe.com https://*.smartlook.com https://*.smartlook.cloud; connect-src 'self' https://sentry.snowfall.se https://js.stripe.com https://*.smartlook.com https://*.smartlook.cloud; img-src 'self' data: blob: https://www.gravatar.com https://img.youtube.com; font-src 'self' data: https://fonts.gstatic.com https://www.slant.co; frame-src 'self' https://js.stripe.com https://www.youtube.com https://*.smartlook.com https://*.smartlook.cloud",
        "traefik.http.middlewares.hub-web-${var.environment}-headers.headers.contenttypenosniff=true",
        "traefik.http.middlewares.hub-web-${var.environment}-headers.headers.customresponseheaders.Permissions-Policy=geolocation=(self), payment=(self)",
        "traefik.http.middlewares.hub-web-${var.environment}-headers.headers.forceSTSHeader=true",
        "traefik.http.middlewares.hub-web-${var.environment}-headers.headers.framedeny=true",
        "traefik.http.middlewares.hub-web-${var.environment}-headers.headers.referrerpolicy=strict-origin-when-cross-origin",
        "traefik.http.middlewares.hub-web-${var.environment}-headers.headers.stsincludesubdomains=true",
        "traefik.http.middlewares.hub-web-${var.environment}-headers.headers.stspreload=true",
        "traefik.http.middlewares.hub-web-${var.environment}-headers.headers.stsseconds=63072000",
        "traefik.http.routers.hub-web-${var.environment}.middlewares=hub-web-${var.environment}-headers",
        "traefik.http.routers.hub-web-${var.environment}.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.hub-web-${var.environment}.rule=Host(`${var.traefik_host_URL}`)"
      ]

      connect {
        sidecar_service {
          proxy {
            upstreams {
              local_bind_port  = 8010
              destination_name = "client-api-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8020
              destination_name = "booking-hub-mobile-api-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8030
              destination_name = "hub-api-${var.environment}"
            }
          }
        }
      }

      check {
        type     = "http"
        path     = "/"
        interval = "30s"
        timeout  = "4s"
      }
    }

    task "http" {
      driver = "docker"

      vault {
        policies = ["hub-web-${var.environment}"]
      }

      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
{{ with secret "kv/data/${var.environment}/hub-web" }}
JWT_SECRET={{ .Data.data.jwt_secret }}
PUBLIC_STRIPE_KEY={{ .Data.data.public_stripe_key }}
PUBLIC_SMARTLOOK_PROJECT_KEY={{ .Data.data.public_smartlook_project_key }}
{{ end }}
CLIENT_API_BASE_URL={{(printf "http://%s" (env "NOMAD_UPSTREAM_ADDR_client-api-${var.environment}"))}}
HUB_API_BASE_URL={{(printf "http://%s" (env "NOMAD_UPSTREAM_ADDR_hub-api-${var.environment}"))}}
BOOKING_HUB_API_BASE_URL={{(printf "http://%s" (env "NOMAD_UPSTREAM_ADDR_booking-hub-mobile-api-${var.environment}"))}}
EOH
      }

      config {
        image = var.docker_image
        ports = ["http"]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {
        ENV_NAME          = "${var.environment}"
        PORT              = "${NOMAD_PORT_http}"
        ORY_BASE_URL      = "${var.ory_base_url}"
        PUBLIC_SENTRY_DSN = "https://33b134d137c04fb8ba77aabdbd60304c@sentry.snowfall.se/68"
      }
    }
  }
}
