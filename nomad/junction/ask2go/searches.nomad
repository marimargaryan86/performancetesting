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

job "ask2go-searches" {
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

    task "searches" {
      driver = "docker"

      vault {
        policies = ["ask2go-development"]
      }

      template {
        data        = <<EOH
AMQP_DSN={{range $index, $service := service "amqp"}}amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}// {{end}}
REDIS_DSN={{range $index, $service := service "redis"}}redis://{{.Address}}:{{.Port}}// {{end}}
{{ with secret (printf "kv/data/%s/ask2go" (env "NOMAD_NAMESPACE")) }}
POLL_RETRIES_LIMIT={{ .Data.data.poll_retries_limit }}
WAIT_TIME_BETWEEN_POLLING={{ .Data.data.wait_time_between_polling }}
{{ end }}
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = var.docker_image
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
        API_BASE_URL         = "http://ec2-18-194-173-6.eu-central-1.compute.amazonaws.com"
        API_BOOKING_BASE_URL = "http://ec2-3-68-186-171.eu-central-1.compute.amazonaws.com"
        ENV_NAME             = "${NOMAD_NAMESPACE}"
        SENTRY_DSN           = "https://c299617e39d446ccb1053a04d9ac12b8@sentry.snowfall.se/34"
      }
    }
  }
}
