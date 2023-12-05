variable "datacenter" {
  type = string
}
variable "environment" {
  type = string
}
variable "registry_address" {
  type = string
}
variable "registry_password" {
  type = string
}
variable "registry_username" {
  type = string
}
variable "traefik_host_URL" {
  type = string
}
variable "traefik_entrypoints" {
  type = string
}

job "vendor-thumbor-http" {

  datacenters = ["${var.datacenter}"]
  type        = "service"

  update {
    max_parallel      = 1
    auto_revert       = true
    auto_promote      = true
    canary            = 1
    healthy_deadline  = "2m"
    progress_deadline = "4m"
  }

  group "http" {
    count = 2

    network {
      port "http" {
        to = 8888
      }
    }

    service {
      name = "thumbor-http"
      port = "http"
      tags = [
        "http",
        "traefik.enable=true",
        "traefik.http.routers.thumbor-http.entrypoints=${var.traefik_entrypoints}",
        "traefik.http.routers.thumbor-http.rule=Host(`${var.traefik_host_URL}`)",
      ]

    }

    task "http" {
      driver = "docker"

      resources {
        memory = 512
      }
      vault {
        policies = ["thumbor-${var.environment}"]
      }

      template {
        destination = "services.env"
        env         = true
        change_mode = "restart"
        data        = <<EOH
{{ with secret "kv/data/${var.environment}/thumbor" }}
SECURITY_KEY={{ .Data.data.security_key }}
AWS_STORAGE_S3_SECRET_ACCESS_KEY={{ .Data.data.aws_storage_s3_secret_access_key }}
AWS_STORAGE_S3_ACCESS_KEY_ID={{ .Data.data.aws_storage_s3_access_key_id }}
AWS_RESULT_STORAGE_S3_SECRET_ACCESS_KEY={{ .Data.data.aws_result_storage_s3_secret_access_key }}
AWS_RESULT_STORAGE_S3_ACCESS_KEY_ID={{ .Data.data.aws_result_storage_s3_access_key_id }}
AWS_STORAGE_BUCKET_NAME={{ .Data.data.aws_storage_bucket_name }}
AWS_STORAGE_S3_ENDPOINT_URL={{ .Data.data.aws_storage_s3_endpoint_url }}
AWS_DEFAULT_LOCATION={{ .Data.data.aws_default_location }}
AWS_RESULT_STORAGE_BUCKET_NAME={{ .Data.data.aws_result_storage_bucket_name }}
AWS_RESULT_STORAGE_S3_ENDPOINT_URL={{ .Data.data.aws_result_storage_s3_endpoint_url }}
{{ end }}
EOH
      }

      config {
        image = "git.snowfall.se:4567/devops/thumbor:3cf9d573c9ec321629163ab0ff90f4d92741162e"
        ports = ["http"]

        auth {
          username       = var.registry_username
          password       = var.registry_password
          server_address = var.registry_address
        }
      }

      env {

        HTTP_LOADER_VALIDATE_CERTS     = "False"
        PORT                           = "${NOMAD_PORT_http}"
        ALLOW_UNSAFE_URL               = "True"
        FORWARDED_ALLOWED_IPS          = "0.0.0.0"
        ENV_NAME                       = "${NOMAD_NAMESPACE}"
        HTTP_ADDRESS                   = "0.0.0.0"
        AUTO_WEBP                      = "True"
        LOADER                         = "thumbor.loaders.http_loader"
        STORAGE                        = "thumbor_aws.storage"
        RESULT_STORAGE                 = "thumbor_aws.result_storage"
        AWS_STORAGE_REGION_NAME        = "eu-west-2"
        AWS_STORAGE_ROOT_PATH          = "storage"
        AWS_RESULT_STORAGE_REGION_NAME = "eu-west-2"
        AWS_RESULT_STORAGE_ROOT_PATH   = "storage"
        ALLOW_OLD_URLS                 = "True"

      }
    }
  }
}

