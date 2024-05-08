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

variable "j_one_api_base_url" {
  type = string
}

variable "j_one_pay_company_id" {
  type = string
}

job "junction-rocket-api-pricing" {
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

  group "pricing" {
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
              destination_name = "transactions-${var.environment}"
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

    task "pricing" {
      driver = "docker"

      vault {
        policies = ["rocket-api-${var.environment}"]
      }

      template {
        data        = <<EOH
AMQP_DSN={{range $index, $service := service "amqp-${var.environment}"}}amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}// {{end}}
{{ with secret "kv/data/${var.environment}/rocket-api" }}
J_ONE_API_KEY={{ .Data.data.j_one_api_key }}
{{ end }}
MONGO_DSN={{range $index, $service := service "mongodb-${var.environment}"}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}
TRANSACTIONS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_transactions-${var.environment}"))}}
RESELLER_J1_CREDENTIALS_MAPPING={{keyOrDefault "${var.environment}/rocket-api/reseller-j1-credentials-mapping" "{}" | toJSON }}
REDIS_DSN={{range $index, $service := service "redis-${var.environment}"}}redis://{{.Address}}:{{.Port}}// {{end}}
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = var.docker_image
        ports = ["prometheus"]
        args = [
          "pricing",
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {
        ENV_NAME             = "${var.environment}"
        SENTRY_DSN           = "https://303cafc116e642efe7c538795b0c2e7a@sentry.snowfall.se/238"
        PROMETHEUS_PORT      = "${NOMAD_PORT_prometheus}"
        J_ONE_API_BASE_URL   = "${var.j_one_api_base_url}"
        J_ONE_PAY_COMPANY_ID = "${var.j_one_pay_company_id}"
      }
    }
  }
}
