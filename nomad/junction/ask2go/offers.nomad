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

job "ask2go-offers" {
  datacenters = ["${var.datacenter}"]
  type        = "service"

  update {
    max_parallel      = 1
    auto_revert       = true
    auto_promote      = true
    canary            = 1
    healthy_deadline  = "30s"
    progress_deadline = "2m"
  }

  group "offers" {
    count = 2

    network {
      mode = "bridge"
      port "prometheus" {}
    }

    service {
      name = "ask2go-offers-${var.environment}"
      port = "prometheus"
      tags = ["metrics"]

      connect {
        sidecar_service {}
      }

      check {
        type     = "http"
        path     = "/"
        interval = "10s"
        timeout  = "2s"
      }
    }
    task "offers" {
      driver = "docker"

      template {
        data        = <<EOH
AMQP_DSN={{range $index, $service := service "amqp-${var.environment}"}}amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}// {{end}}
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = var.docker_image
        ports = ["prometheus"]
        args = [
          "offers",
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
        ENV_NAME             = "${var.environment}"
        SENTRY_DSN           = "https://c299617e39d446ccb1053a04d9ac12b8@sentry.snowfall.se/34"
        PROMETHEUS_PORT      = "${NOMAD_PORT_prometheus}"
      }
    }
  }
}
