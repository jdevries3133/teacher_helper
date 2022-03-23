# Infrastructure for documentation site

terraform {
  backend "s3" {
    bucket = "my-sites-terraform-remote-state"
    key    = "teacher_helper_docs"
    region = "us-east-2"
  }

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.7.1"
    }
  }
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}

data "external" "git_describe" {
  program = ["sh", "scripts/git_describe.sh"]
}

module "deployment" {
  source  = "jdevries3133/container-deployment/kubernetes"
  version = "0.2.0"

  app_name  = "teacher-helper-docs"
  container = "jdevries3133/teacher_helper_docs:${data.external.git_describe.result.output}"
  domain    = "teacherhelper.jackdevries.com"
}
