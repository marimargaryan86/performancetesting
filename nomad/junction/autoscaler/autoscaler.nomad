variable "environment" {
  type = string
}

variable "datacenter" {
  type = string
}

job "autoscaler" {
  datacenters = ["${var.datacenter}"]
  type        = "service"
  namespace   = "monitoring"

  group "autoscaler" {
    count = 1

    network {
      port "http" {}
    }

    task "autoscaler" {
      driver = "docker"

      config {
        image   = "hashicorp/nomad-autoscaler:0.3.7"
        command = "nomad-autoscaler"
        ports   = ["http"]

        args = [
          "agent",
          "-config",
          "${NOMAD_TASK_DIR}/config.hcl",
          "-http-bind-address",
          "0.0.0.0",
          "-http-bind-port",
          "${NOMAD_PORT_http}",
        ]
      }
      vault {
        policies = ["autoscaler-${var.environment}"]
      }
      template {
        data        = <<EOF
nomad {
  address = "{{ with service "nomad-client" }}{{ with index . 0 }}http://{{.Address}}:{{.Port}}{{ end }}{{ end }}"
  namespace = "*"
}

telemetry {
  prometheus_metrics = true
  disable_hostname   = true
}

apm "prometheus" {
  driver = "prometheus"
  config = {
    address = "http://prometheus.snowfall.se"
{{ with secret "kv/data/${var.environment}/autoscaler" }}
basic_auth_user     = "{{ .Data.data.basic_auth_user }}"
basic_auth_password = "{{ .Data.data.basic_auth_password }}"
{{ end }}
  }
}

strategy "target-value" {
  driver = "target-value"
}
          EOF
        destination = "${NOMAD_TASK_DIR}/config.hcl"
      }

      resources {
        cpu    = 150
        memory = 240
      }

      service {
        name     = "autoscaler"
        provider = "nomad"
        port     = "http"

        check {
          type     = "http"
          path     = "/v1/health"
          interval = "3s"
          timeout  = "1s"
        }
      }
    }
  }
}
