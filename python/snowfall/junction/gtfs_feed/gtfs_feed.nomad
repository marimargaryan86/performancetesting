job "gtfs_feed" {
  datacenters = ["junction-dev-dc1"]
  type = "batch"

  periodic {
    cron = "@daily"
    prohibit_overlap = true
  }

  group "gtfs_feed" {
    count = 1

    ephemeral_disk {
      size = 1000
    }

    task "sweden" {
      driver = "docker"

      config {
        image = "${DOCKER_IMAGE}"

        auth {
          username = "${NOMAD_REGISTRY_USERNAME}"
          password = "${NOMAD_REGISTRY_PASSWORD}"
          server_address = "${CI_REGISTRY}"
        }
      }

      env {
        FEED_URL = "https://transitfeeds.com/p/trafiklab/50/latest/download"
      }
    }
  }
}
