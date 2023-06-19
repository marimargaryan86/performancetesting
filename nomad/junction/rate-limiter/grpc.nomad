variable "datacenter" {
  type = string
}

variable "environment" {
  type = string
}

variable "count" {
  type = number
}

job "rate-limiter-grpc" {
  datacenters = ["${var.datacenter}"]
  type        = "service"


  update {
    max_parallel      = 1
    auto_revert       = true
    auto_promote      = true
    canary            = 1
    healthy_deadline  = "1m"
    progress_deadline = "2m"
  }

  group "grpc" {
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
      port "grpc" {}
    }

    service {
      name = "rate-limiter-grpc-${var.environment}"
      port = "grpc"
      tags = ["grpc"]

      connect {
        sidecar_service {}
      }
    }

    service {
      name = "rate-limiter-http-${var.environment}"
      port = "http"
      tags = ["http"]

      check {
        type     = "http"
        path     = "/v1/HealthCheck"
        interval = "30s"
        timeout  = "4s"
      }
    }

    task "grpc" {
      driver = "docker"

      resources {
        memory = 200
      }

      config {
        image = "ghcr.io/mailgun/gubernator:v2.0.0-rc.46"
        ports = ["http", "grpc"]
      }

      env {
        ENV_NAME              = "${var.environment}"
        OTEL_METRICS_EXPORTER = "none"
        OTEL_TRACES_EXPORTER  = "none"
        GUBER_GRPC_ADDRESS    = "0.0.0.0:${NOMAD_PORT_grpc}"
        GUBER_HTTP_ADDRESS    = "0.0.0.0:${NOMAD_PORT_http}"
        #GUBER_DEBUG           = "true"
      }
    }
  }
}
