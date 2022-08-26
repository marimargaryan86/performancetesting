job "prometheus" {
  datacenters = ["junction-dev-dc1"]
  type        = "service"
  namespace   = "monitoring"

  group "monitoring" {
    count = 1

    network {
      port "prometheus_ui" {
        static = 9090
      }
    }

    restart {
      attempts = 2
      interval = "30m"
      delay    = "15s"
      mode     = "fail"
    }

    ephemeral_disk {
      size = 300
    }

    task "prometheus" {
      template {
        change_mode = "restart"
        destination = "${NOMAD_TASK_DIR}/prometheus.yml"
        data        = <<EOH

global:
  scrape_interval:     5s
  evaluation_interval: 5s

scrape_configs:
  - job_name: "consul"
    consul_sd_configs:
      - server: '{{ env "NOMAD_IP_prometheus_ui" }}:8500'
    relabel_configs:
      - regex: __meta_consul_service_metadata_(.+)
        action: labelmap
      - source_labels: [__meta_consul_tags]
        regex: (.*)metrics(.*)
        action: keep
      - source_labels: [__meta_consul_service]
        target_label: job
      - source_labels: [__meta_consul_node]
        target_label: instance
    scrape_interval: 5s
    params:
      format: ['prometheus']

EOH
      }

      driver = "docker"

      config {
        image = "prom/prometheus:latest"
        ports = ["prometheus_ui"]
        args  = ["--config.file=${NOMAD_TASK_DIR}/prometheus.yml"]
      }

      service {
        name = "prometheus"
        port = "prometheus_ui"

        check {
          type     = "http"
          path     = "/-/healthy"
          interval = "10s"
          timeout  = "2s"
        }
      }
    }
  }
}