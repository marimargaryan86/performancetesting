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

variable "api_base_url" {
  type = string
}

variable "api_booking_base_url" {
  type = string
}

variable "queue_name" {
  type = string
}

variable "endpoint_url" {
  type = string
}

variable "aws_region" {
  type = string
}

job "ask2go-order-changes" {
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

  group "order-changes" {
    count = "${var.count}"

    restart {
      attempts = 3
      delay    = "15s"
      interval = "10m"
      mode     = "delay"
    }

    network {
      mode = "bridge"
      port "grpc" {}
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

      check {
        type     = "http"
        path     = "/"
        interval = "30s"
        timeout  = "4s"
      }
    }
    task "order-changes" {
      driver = "docker"
      vault {
        policies = ["ask2go-${var.environment}"]
      }

      template {
        data        = <<EOH
{{ with secret "kv/data/${var.environment}/ask2go" }}
A2G_SQS_AWS_ACCESS_KEY_ID={{ .Data.data.a2g_sqs_aws_access_key_id }}
A2G_SQS_AWS_SECRET_ACCESS_KEY={{ .Data.data.a2g_sqs_aws_secret_access_key }}
{{ end }}
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = var.docker_image
        ports = ["grpc", "prometheus"]
        args = [
          "order_changes",
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {
        ENV_NAME                  = "${var.environment}"
        SENTRY_DSN                = "https://c299617e39d446ccb1053a04d9ac12b8@sentry.snowfall.se/34"
        PROMETHEUS_PORT           = "${NOMAD_PORT_prometheus}"
        API_BASE_URL              = "${var.api_base_url}"
        API_BOOKING_BASE_URL      = "${var.api_booking_base_url}"
        QUEUE_NAME                = "${var.queue_name}"
        ENDPOINT_URL              = "${var.endpoint_url}"
        AWS_REGION                = "${var.aws_region}"
        WAIT_TIME_BETWEEN_POLLING = "20"
      }
    }
  }
}
