variable "datacenter" {
  type = string
}
variable "environment" {
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
variable "traefik_host_URL" {
  type = string
}
variable "traefik_entrypoints" {
  type = string
}

variable "docker_image" {
  type = string
}

variable "pss_v1_dsn" {
  type = string
}

variable "count" {
  type = number
}

job "pss-api-v2-http" {

  datacenters = ["${var.datacenter}"]
  type        = "service"

  update {
    max_parallel      = 1
    auto_revert       = true
    auto_promote      = true
    canary            = 1
    healthy_deadline  = "100s"
    progress_deadline = "2m"
  }

  group "http" {

    count = "${var.count}"

    network {
      port "http" {
        to = 8888
      }
    }

    service {
      name = "pss-api-v2"
      port = "http"
      tags = [
        "http",
        "traefik.enable=true",
        "traefik.http.routers.pss-api-v2.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.pss-api-v2.rule=Host(`${var.traefik_host_URL}`)",
      ]

    }

    task "http" {
      driver = "docker"

      vault {
        policies = ["pss-api-v2-${var.environment}"]
      }

      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
SMTP_DSN={{range $index, $service := service "smtp"}}smtp://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}{{end}}
{{ with secret "kv/data/${var.environment}/pss-api-v2" }}
MYSQL_DSN={{ .Data.data.mysql_dsn }}
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

        ENV_NAME     = "${var.environment}"
        HTTP_ADDRESS = "0.0.0.0"
        HTTP_PORT    = "${NOMAD_PORT_http}"
        SENTRY_DSN   = "https://c674550aaa124dd9b5f02bf6c49b1983@sentry.snowfall.se/60"
        SMTP_SENDER  = "no-reply@snowfall.se"
        WEB_DSN      = "https://web.spex.snowfalltravel.com/"
        PSS_V1_DSN   = "${var.pss_v1_dsn}"
      }
    }
  }
}
