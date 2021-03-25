provider "aws" {
  region  = var.aws_region
  version = "~> 2.65"
}

provider "random" {
  version = "2.2.1"
}

terraform {
  required_providers {
    kubernetes = {
      source = "hashicorp/kubernetes"
    }
  }
}
