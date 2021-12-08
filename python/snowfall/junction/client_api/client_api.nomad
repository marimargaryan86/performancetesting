job "client-api" {
  datacenters = ["junction-dev-dc1"]
  type = "service"

  update {
    max_parallel = 1
    auto_revert = true
    auto_promote = true
    canary = 1
  }

  group "client-api" {
    count = 1

    network {
      port "http" {}
    }

    service {
      name = "client-api"
      port = "http"

      check {
        type     = "http"
        path     = "/health"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "client-api" {
      driver = "docker"

      config {
        image = "${DOCKER_IMAGE}"
        ports = ["http"]

        auth {
          username = "${CI_REGISTRY_USER}"
          password = "${CI_REGISTRY_PASSWORD}"
          server_address = "${CI_REGISTRY}"
        }
      }

      env {
        HTTP_ADDRESS = "${NOMAD_IP_http}"
        HTTP_PORT = "${NOMAD_PORT_http}"
      }
    }
  }
}
