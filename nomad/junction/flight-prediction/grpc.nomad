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

job "flight-prediction-grpc" {
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
  group "grpc" {
    count = "${var.count}"

    restart {
      attempts = 3
      delay    = "15s"
      interval = "10m"
      mode     = "delay"
    }

    scaling {
      enabled = false
      min     = 1
      max     = 20
    }

    network {
      mode = "bridge"
      port "grpc" {}
      port "prometheus" {}
    }

    service {
      name = "flight-prediction-${var.environment}"
      port = "grpc"
      tags = ["grpc"]

      connect {
        sidecar_service {}
      }

      check {
        type     = "grpc"
        interval = "30s"
        timeout  = "4s"
      }
    }

    service {
      name = "flight-prediction-${var.environment}"
      port = "prometheus"
      tags = ["metrics"]

      check {
        type     = "http"
        path     = "/"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "grpc" {
      driver = "docker"

      vault {
        policies = ["flight-prediction-${var.environment}"]
      }

      template {
        data        = <<EOH
{{ with secret "kv/data/${var.environment}/flight-prediction" }}
AWS_ACCESS_KEY_ID={{ .Data.data.aws_access_key_id }}
AWS_SECRET_ACCESS_KEY={{ .Data.data.aws_secret_access_key }}
FLIGHT_STATS_APP_ID={{ .Data.data.flight_stats_app_id }}
FLIGHT_STATS_APP_KEY={{ .Data.data.flight_stats_app_key }}
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
          "grpc",
        ]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {
        ENV_NAME                    = "${var.environment}"
        GRPC_ADDRESS                = "0.0.0.0"
        GRPC_PORT                   = "${NOMAD_PORT_grpc}"
        SENTRY_DSN                  = "https://6ce65492acd4484caa731dd1073fe114@sentry.snowfall.se/172"
        PROMETHEUS_PORT             = "${NOMAD_PORT_prometheus}"
        FLIGHT_STATS_API_URL        = "https://api.flightstats.com/flex/flightstatus/rest/v2/json/flight/status/"
        AWS_SAGEMAKER_ENDPOINT_NAME = "predictorv2-2"
      }
    }
  }
}

