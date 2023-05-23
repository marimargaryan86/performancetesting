variable "datacenter" {
  type = string
}
variable "environment" {
  type = string
}
variable "vault_api_URL" {
  type = string
}

job "test-automation-pay-api" {

  datacenters = ["${var.datacenter}"]
  priority    = 50
  type        = "batch"

  periodic {
    cron             = "0 8 * * 1-5"
    prohibit_overlap = true
    time_zone        = "Europe/Warsaw"
  }

  group "pay-api" {
    count = 1
    service {
      name = "test-automation-runner-${var.environment}"
    }

    task "pay-api" {
      driver = "docker"
      vault {
        policies = ["api-automation-${var.environment}"]
      }

      resources {
        memory = 100
      }
      template {
        data        = <<EOH
{{ with secret "kv/data/${var.environment}/api-automation" }}
SLACK_NOTIFICATION_TOKEN={{ .Data.data.slack_notifcation_token }}
PIPELINE_GITLAB_TOKEN={{ .Data.data.pipeline_gitlab_token }}
{{ end }}
EOH
        destination = "services.env"
        env         = true
        change_mode = "restart"
      }
      config {
        image = "curlimages/curl"
        args = [
          "-X"
          , "POST"
          , "--fail"
          , "-F"
          , "token=${PIPELINE_GITLAB_TOKEN}"
          , "-F"
          , "ref=main"
          , "-F"
          , "variables[HOSTNAME]=${var.vault_api_URL}"
          , "-F"
          , "variables[ALLURE_PROJECT_ID]=junction-pay-api-smoke"
          , "-F"
          , "variables[SLACK_NOTIFICATION_CHANNEL]=junction-pay-dev"
          , "-F"
          , "variables[SLACK_NOTIFICATION_TOKEN]=${SLACK_NOTIFICATION_TOKEN}"
          , "-F"
          , "variables[API_TOKEN]=JUNCTION_TEST_VAULT_TOKEN"
          , "-F"
          , "variables[PROJECT_NAME]=api_automation"
          , "-F"
          , "variables[PROJECT_DIR]=pay_api_tests/"
          , "-F"
          , "variables[CI_PIPELINE_SOURCE]=schedule"
          , "https://git.snowfall.se/api/v4/projects/406/trigger/pipeline"
        ]
      }
    }
  }
}
