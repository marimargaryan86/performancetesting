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

job "save-a-train-searches" {
  datacenters = ["junction-dev-dc1"]
  type        = "service"

  update {
    max_parallel      = 1
    auto_revert       = true
    auto_promote      = true
    canary            = 1
    healthy_deadline  = "30s"
    progress_deadline = "2m"
  }

  group "searches" {
    count = 5

    network {
      port "prometheus" {}
    }

    service {
      name = "save-a-train-${NOMAD_NAMESPACE}"
      port = "prometheus"
      tags = ["metrics"]

      check {
        type     = "http"
        path     = "/"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "searches" {
      driver = "docker"

      vault {
        policies = ["save-a-train-development"]
      }

      template {
        data        = <<EOH
AMQP_DSN={{range $index, $service := service "amqp"}}amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}// {{end}}
GEODATA_ADDRESS={{range $index, $service := service (printf "grpc.geodata-%s" (env "NOMAD_NAMESPACE"))}}{{.Address}}:{{.Port}} {{end}}
REDIS_DSN={{range $index, $service := service "redis"}}redis://{{.Address}}:{{.Port}}// {{end}}
{{ with secret (printf "kv/data/%s/save-a-train" (env "NOMAD_NAMESPACE")) }}
API_EMAIL={{ .Data.data.api_email }}
API_PASSWORD={{ .Data.data.api_password }}
API_SEARCH_PASSWORD={{ .Data.data.api_search_password }}
API_BOOKING_TOKEN={{ .Data.data.api_booking_token }}
{{ end }}
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = var.docker_image
        ports = ["prometheus"]
        args = [
          "searches",
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {
        API_BASE_URL        = "https://satvendorstest.saveatrain.com/api/"
        API_SEARCH_BASE_URL = "https://apisearch.saveatrain.com/search"
        ENV_NAME            = "${NOMAD_NAMESPACE}"
        SENTRY_DSN          = "https://f01c7c8bf4d04a709a65b4be8b11ba69@sentry.snowfall.se/36"
        PROMETHEUS_PORT     = "${NOMAD_PORT_prometheus}"
      }
    }
  }
}