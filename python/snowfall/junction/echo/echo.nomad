job "echo" {
  datacenters = ["junction-dev-dc1"]
  type = "service"

  update {
    max_parallel = 1
    auto_revert = true
    auto_promote = true
    canary = 1
  }

  group "echo" {
    count = 1

    network {
      port "grpc" {}
    }

    service {
      name = "echo"
      port = "grpc"

      check {
        type     = "grpc"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "echo" {
      driver = "docker"

      config {
        image = "${DOCKER_IMAGE}"
        ports = ["grpc"]

        auth {
          username = "${CI_REGISTRY_USER}"
          password = "${CI_REGISTRY_PASSWORD}"
          server_address = "${CI_REGISTRY}"
        }
      }

      env {
        GRPC_PORT = "${NOMAD_PORT_grpc}"
      }
    }
  }
}
