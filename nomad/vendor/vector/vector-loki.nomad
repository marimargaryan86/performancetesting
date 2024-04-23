variable "loki_endpoint" {
  type = string
}

variable "datacenter" {
  type = string
}


job "vendor-vector-vector-loki" {
  datacenters = ["${var.datacenter}"]
  namespace   = "monitoring"
  type        = "system"
  update {
    min_healthy_time  = "10s"
    healthy_deadline  = "5m"
    progress_deadline = "10m"
    auto_revert       = true
  }
  group "vector-loki" {
    count = 1
    restart {
      attempts = 3
      delay    = "15s"
      interval = "10m"
      mode     = "delay"
    }
    network {
      port "api" {
        to = 8686
      }
    }
    ephemeral_disk {
      size   = 500
      sticky = true
    }
    task "vector-loki" {
      driver = "docker"
      config {
        image = "timberio/vector:0.32.0-alpine"
        ports = ["api"]

        volumes = [
          "/var/run/docker.sock:/var/run/docker.sock",
          "/var/lib/docker/containers:/var/lib/docker/containers"
        ]
      }
      env {
        VECTOR_CONFIG          = "local/vector.toml"
        VECTOR_REQUIRE_HEALTHY = "true"
      }
      resources {
        memory = 200 # 200MB
      }
      template {
        destination   = "local/vector.toml"
        change_mode   = "signal"
        change_signal = "SIGHUP"
        # overriding the delimiters to [[ ]] to avoid conflicts with Vector's native templating, which also uses {{ }}
        left_delimiter  = "[["
        right_delimiter = "]]"
        data            = <<EOH
          data_dir = "alloc/data/vector/"
          [api]
            enabled = true
            address = "0.0.0.0:8686"
            playground = true
          [sources.logs]
            type = "docker_logs"
          [transforms.relabel_docker_logs]
            inputs = ["logs"]
            type   = "remap"
            source = """
            .message,err = parse_json(.message)
            .log_level = .message.level
            .service_name = replace(.label."com.hashicorp.nomad.job_name",r'/periodic-(\\d+)',"") ?? ""
          """
          [transforms.elastic_transform]
            inputs = ["logs"]
            type   = "remap"
            source = """
            .message,err = parse_json(.message)
            .log_level = .message.level
            .service_name = replace(.label."com.hashicorp.nomad.job_name",r'/periodic-(\\d+)',"") ?? ""
            del(.label.\"com.hashicorp.nomad.job_name\")
            .task = del(.label.\"com.hashicorp.nomad.task_name\")
            .group = del(.label.\"com.hashicorp.nomad.task_group_name\")
            .namespace = del(.label.\"com.hashicorp.nomad.namespace\")
            .node = del(.label.\"com.hashicorp.nomad.node_name\")
            .alloc_id = del(.label.\"com.hashicorp.nomad.alloc_id\")
            .version = del(.label.\"com.snowfalltravel.version\")
            .job = "${var.datacenter}"
          """
          [sinks.loki]
            type = "loki"
            inputs = ["relabel_docker_logs"]
            endpoint = "${var.loki_endpoint}"
            encoding.codec = "json"
            healthcheck.enabled = true
            # since . is used by Vector to denote a parent-child relationship, and Nomad's Docker labels contain ".",
            # we need to escape them twice, once for TOML, once for Vector
            labels.task = "{{ label.\"com.hashicorp.nomad.task_name\" }}"
            labels.group = "{{ label.\"com.hashicorp.nomad.task_group_name\" }}"
            labels.namespace = "{{ label.\"com.hashicorp.nomad.namespace\" }}"
            labels.node = "{{ label.\"com.hashicorp.nomad.node_name\" }}"
            labels.job = "${var.datacenter}"
            labels.stream = "{{ stream }}"
            labels.log_level = "{{ log_level }}"
            labels.service_name = "{{ service_name}}"
            #remove fields that have been converted to labels to avoid having the field twice
            remove_label_fields = true
          [sinks.elk]
            type = "elasticsearch"
            inputs = ["elastic_transform"]
            compression = "none"
            bulk.index = "vector-${var.datacenter}-%Y-%m-%d"
            endpoints = ["http://172.16.111.145:9200"]
            healthcheck.enabled = true

        EOH
      }

      service {
        check {
          port     = "api"
          type     = "http"
          path     = "/health"
          interval = "30s"
          timeout  = "4s"
        }
      }
      kill_timeout = "30s"
    }
  }
}
