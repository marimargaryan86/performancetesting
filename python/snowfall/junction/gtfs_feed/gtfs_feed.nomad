job "gtfs-feed" {
  datacenters = ["junction-dev-dc1"]
  type = "batch"

  periodic {
    cron = "@daily"
    prohibit_overlap = true
  }

  group "gtfs-feed" {
    count = 1

    ephemeral_disk {
      size = 1000
    }

    task "belgium" {
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
        FEED_URL = "https://gtfs.irail.be/nmbs/gtfs/latest.zip"
      }
    }

    task "denmark" {
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
        FEED_URL = "http://www.rejseplanen.info/labs/GTFS.zip"
      }
    }

    task "netherlands" {
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
        FEED_URL = "http://gtfs.ovapi.nl/gtfs-nl.zip"
      }
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
