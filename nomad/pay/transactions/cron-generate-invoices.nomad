variable "docker_image" {
  type = string
}

variable "registry_address" {
  type = string
}

variable "registry_password" {
  type = string
}

variable "bucket" {
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

job "pay-transactions-cron-generate-invoices" {
  datacenters = ["${var.datacenter}"]
  type        = "batch"

  periodic {
    cron             = "@daily"
    prohibit_overlap = true
  }

  group "cron-generate-invoices" {
    count = 1

    restart {
      attempts = 3
      delay    = "5m"
      interval = "20m"
      mode     = "delay"
    }

    network {
      mode = "bridge"
      port "grpc" {}
    }

    service {
      name = "generate-invoices-${var.environment}"
      port = "grpc"
      tags = ["grpc"]

      connect {
        sidecar_service {
          proxy {
            upstreams {
              local_bind_port  = 8010
              destination_name = "credit-card-payments-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8020
              destination_name = "companies-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8030
              destination_name = "resellers-${var.environment}"
            }
            upstreams {
              local_bind_port  = 8040
              destination_name = "orders-${var.environment}"
            }
          }
        }
      }

      check {
        type     = "grpc"
        interval = "30s"
        timeout  = "4s"
      }
    }

    task "cron-generate-invoices" {
      driver = "docker"

      vault {
        policies = ["transactions-reports-cron-${var.environment}"]
      }

      template {
        data        = <<EOH
MONGO_DSN={{range $index, $service := service "mongodb-${var.environment}"}}mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}} {{end}}
SMTP_DSN={{range $index, $service := service "smtp"}}smtp://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}{{end}}
COMPANIES_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_companies-${var.environment}"))}}
RESELLERS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_resellers-${var.environment}"))}}
CREDIT_CARD_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_credit-card-payments-${var.environment}"))}}
ORDERS_ADDRESS={{(printf "%s" (env "NOMAD_UPSTREAM_ADDR_orders-${var.environment}"))}}
{{ with secret "kv/data/${var.environment}/transactions-reports-cron" }}
STORAGE_DSN=s3://{{ .Data.data.aws_access_key_id }}:{{ .Data.data.aws_secret_access_key | urlquery }}@/${var.bucket}/invoices
{{ end }}
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = var.docker_image
        args = [
          "cron-generate-invoices"
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }


      env {
        ENV_NAME   = "${var.environment}"
        SENTRY_DSN = "https://0c052cf147584d4391a5243202168e20@sentry.snowfall.se/153"
        PAY_EMAIL  = "pay@snowfalltravel.com"
      }
    }
  }
}
