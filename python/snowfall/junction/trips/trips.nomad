job "trips" {
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

  group "grpc" {
    count = 1

    network {
      port "grpc" {}
    }

    service {
      name = "trips"
      port = "grpc"
      tags = ["grpc"]

      check {
        type     = "grpc"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "grpc" {
      driver = "docker"

      template {
        data        = <<EOH
AMQP_DSN="[{{range $index, $service := service "amqp"}}{{if ne $index 0}},{{end}}\"amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}//\"{{end}}]"
MONGO_DSN="[{{range $index, $service := service "mongodb"}}{{if ne $index 0}},{{end}}\"mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}}\"{{end}}]"
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = "${DOCKER_IMAGE}"
        ports = ["grpc"]
        args = [
          "grpc",
        ]

        auth {
          username       = "${NOMAD_REGISTRY_USERNAME}"
          password       = "${NOMAD_REGISTRY_PASSWORD}"
          server_address = "${CI_REGISTRY}"
        }
      }

      env {
        ENV_NAME     = "development"
        GRPC_ADDRESS = "0.0.0.0"
        GRPC_PORT    = "${NOMAD_PORT_grpc}"
        SENTRY_DSN   = "https://9f6821dca30141bd8f3dc919b7806f6c@sentry.snowfall.se/26"
      }
    }
  }

  group "consume" {
    count = 1

    task "consume" {
      driver = "docker"

      template {
        data        = <<EOH
AMQP_DSN="[{{range $index, $service := service "amqp"}}{{if ne $index 0}},{{end}}\"amqps://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}//\"{{end}}]"
MONGO_DSN="[{{range $index, $service := service "mongodb"}}{{if ne $index 0}},{{end}}\"mongodb://{{.ServiceMeta.username}}:{{.ServiceMeta.password}}@{{.Address}}:{{.Port}}/?{{.ServiceMeta.parameters}}\"{{end}}]"
PLANNER_ADDRESS="[{{range $index, $service := service "grpc.planner"}}{{if ne $index 0}},{{end}}\"{{.Address}}:{{.Port}}\"{{end}}]"
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }

      config {
        image = "${DOCKER_IMAGE}"
        args = [
          "consume",
        ]

        auth {
          username       = "${NOMAD_REGISTRY_USERNAME}"
          password       = "${NOMAD_REGISTRY_PASSWORD}"
          server_address = "${CI_REGISTRY}"
        }
      }

      env {
        ENV_NAME   = "development"
        SENTRY_DSN = "https://9f6821dca30141bd8f3dc919b7806f6c@sentry.snowfall.se/26"
      }
    }
  }
}
