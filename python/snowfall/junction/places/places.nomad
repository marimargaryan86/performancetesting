job "places" {
  datacenters = ["junction-dev-dc1"]
  type = "service"

  update {
    max_parallel = 1
    auto_revert = true
    auto_promote = true
    canary = 1
    healthy_deadline = "30s"
    progress_deadline = "2m"
  }

  group "places" {
    count = 1

    network {
      port "grpc" {}
    }

    service {
      name = "places"
      port = "grpc"
      tags = ["grpc"]

      check {
        type     = "grpc"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "places" {
      driver = "docker"

      config {
        image = "${DOCKER_IMAGE}"
        ports = ["grpc"]

        auth {
          username = "${NOMAD_REGISTRY_USERNAME}"
          password = "${NOMAD_REGISTRY_PASSWORD}"
          server_address = "${CI_REGISTRY}"
        }
      }

      env {
        GRPC_ADDRESS = "0.0.0.0"
        GRPC_PORT = "${NOMAD_PORT_grpc}"
      }
    }
  }
}
