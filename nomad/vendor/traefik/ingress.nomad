variable "datacenter" {
  type = string
}

variable "environment" {
  type = string
}

variable "traefik_entrypoints" {
  type = string
}

variable "static_port" {
  type = number
}

variable "traefik_consul_ui_host_rule" {
  type = string
}

variable "traefik_consul_ui_users" {
  type = list(string)
}

variable "traefik_nomad_ui_host_rule" {
  type = string
}

variable "traefik_nomad_ui_users" {
  type = list(string)
}

variable "traefik_ui_host_rule" {
  type = string
}

variable "traefik_ui_users" {
  type = list(string)
}

variable "traefik_vault_ui_host_rule" {
  type = string
}

variable "traefik_vault_ui_users" {
  type = list(string)
}

variable "ip_whitelist_excludedips" {
  type = list(string)
}

variable "ip_whitelist_sourcerange" {
  type = list(string)
}

job "vendor-traefik-ingress" {
  datacenters = ["${var.datacenter}"]
  type        = "system"
  namespace   = "network"
  priority    = 80

  group "ingress" {
    count = 1

    update {
      max_parallel     = 2
      min_healthy_time = "30s"
      healthy_deadline = "5m"
      auto_revert      = true
    }

    network {
      port "http" {
        static = var.static_port
      }

      port "metrics" {
        static = 8080
      }

      dns {
        servers = [
          "172.17.0.1",
          "1.1.1.1",
          "8.8.8.8"
        ]
      }
    }

    service {
      name = "traefik-ingress-${var.environment}"
      port = "metrics"
      tags = ["metrics"]

      check {
        type     = "http"
        path     = "/metrics"
        interval = "10s"
        timeout  = "2s"
        method   = "HEAD"
      }
    }

    service {
      name = "traefik-junction-${var.environment}-dashboard"
      port = "http"
      tags = [
        "traefik.enable=true",
        "traefik.http.middlewares.traefik-ui-whitelist.ipwhitelist.sourcerange=${join(", ", var.ip_whitelist_sourcerange)}",
        "traefik.http.middlewares.traefik-ui-whitelist.ipwhitelist.ipstrategy.excludedips=${join(", ", var.ip_whitelist_excludedips)}",
        "traefik.http.routers.traefik-ui.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.traefik-ui.rule=${var.traefik_ui_host_rule}",
        "traefik.http.routers.traefik-ui.service=api@internal",
        "traefik.http.middlewares.traefik-ui-auth.basicauth.users=${join(", ", var.traefik_ui_users)}",
        "traefik.http.routers.traefik-ui.middlewares=traefik-ui-whitelist, traefik-ui-auth"
      ]
    }

    service {
      name = "traefik-junction-${var.environment}-nomad-ui"
      port = "http"
      tags = [
        "traefik.enable=true",
        "traefik.http.middlewares.nomad-ui-auth.basicauth.users=${join(", ", var.traefik_nomad_ui_users)}",
        "traefik.http.middlewares.nomad-ui-whitelist.ipwhitelist.sourcerange=${join(", ", var.ip_whitelist_sourcerange)}",
        "traefik.http.middlewares.nomad-ui-whitelist.ipwhitelist.ipstrategy.excludedips=${join(", ", var.ip_whitelist_excludedips)}",
        "traefik.http.routers.nomad-ui.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.nomad-ui.rule=${var.traefik_nomad_ui_host_rule}",
        "traefik.http.routers.nomad-ui.service=junction-${var.environment}-nomad@file",
        "traefik.http.routers.nomad-ui.middlewares=nomad-ui-whitelist, nomad-ui-auth"
      ]
    }

    service {
      name = "traefik-junction-${var.environment}-consul-ui"
      port = "http"
      tags = [
        "traefik.enable=true",
        "traefik.http.middlewares.consul-ui-auth.basicauth.users=${join(", ", var.traefik_consul_ui_users)}",
        "traefik.http.middlewares.consul-ui-whitelist.ipwhitelist.sourcerange=${join(", ", var.ip_whitelist_sourcerange)}",
        "traefik.http.middlewares.consul-ui-whitelist.ipwhitelist.ipstrategy.excludedips=${join(", ", var.ip_whitelist_excludedips)}",
        "traefik.http.routers.consul-ui.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.consul-ui.rule=${var.traefik_consul_ui_host_rule}",
        "traefik.http.routers.consul-ui.service=junction-${var.environment}-consul@file",
        "traefik.http.routers.consul-ui.middlewares=consul-ui-whitelist, consul-ui-auth"
      ]
    }

    service {
      name = "traefik-junction-${var.environment}-vault-ui"
      port = "http"
      tags = [
        "traefik.enable=true",
        "traefik.http.middlewares.vault-ui-auth.basicauth.users=${join(", ", var.traefik_vault_ui_users)}",
        "traefik.http.middlewares.vault-ui-whitelist.ipwhitelist.sourcerange=${join(", ", var.ip_whitelist_sourcerange)}",
        "traefik.http.middlewares.vault-ui-whitelist.ipwhitelist.ipstrategy.excludedips=${join(", ", var.ip_whitelist_excludedips)}",
        "traefik.http.routers.vault-ui.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.vault-ui.rule=${var.traefik_vault_ui_host_rule}",
        "traefik.http.routers.vault-ui.service=junction-${var.environment}-vault@file",
        "traefik.http.routers.vault-ui.middlewares=vault-ui-whitelist, vault-ui-auth"
      ]
    }

    task "ingress" {
      driver = "docker"

      config {
        image      = "traefik:2.10"
        force_pull = true
        ports      = ["http", "metrics"]
        args = [
          "--entrypoints.${var.traefik_entrypoints}.address=:${NOMAD_PORT_http}",
          "--entrypoints.${var.traefik_entrypoints}.forwardedheaders.trustedips=127.0.0.1/32,172.16.0.0/16",
          "--entrypoints.${var.traefik_entrypoints}.http.middlewares=gzip@file",
          "--entrypoints.metrics.address=:${NOMAD_PORT_metrics}",
          "--api=true",
          "--metrics.prometheus.entrypoint=metrics",
          "--metrics.prometheus.addrouterslabels=true",
          "--ping=true",
          "--ping.entrypoint=${var.traefik_entrypoints}",
          "--providers.consulcatalog=true",
          "--providers.consulcatalog.endpoint.address=http://${NOMAD_IP_http}:8500",
          "--providers.consulcatalog.connectaware=true",
          "--providers.consulcatalog.exposedbydefault=false",
          "--providers.file.directory=local/traefik",
          "--log.level=DEBUG",
          "--log.format=json"
          // "--log.level=WARN"
        ]
      }

      template {
        destination = "local/traefik/traefik-config.yml"
        data        = <<EOH
http:
  services:
    junction-${var.environment}-nomad:
      loadbalancer:
        passhostheader: true
        servers:
          - url: "http://nomad.service.consul:4646/"

    junction-${var.environment}-consul:
      loadbalancer:
        passhostheader: true
        servers:
          - url: "http://consul.service.consul:8500/"

    junction-${var.environment}-vault:
      loadbalancer:
        passhostheader: true
        servers:
          - url: "http://vault.service.consul:8200/"

  middlewares:
    gzip:
      compress: {}

    security-headers:
      headers:
        referrerPolicy: strict-origin-when-cross-origin
        stsSeconds: 63072000
        stsIncludeSubdomains: true
        stsPreload: true
        forceSTSHeader: true
        contentTypeNosniff: true
        frameDeny: true
        permissionsPolicy: camera=(), fullscreen=(), microphone=()

    csp-unsafe-headers:
      headers:
        contentSecurityPolicy: "default-src * 'unsafe-inline' 'unsafe-eval' data: blob: filesystem:; frame-ancestors *; form-action *; upgrade-insecure-requests;"
EOH
      }
    }
  }
}
