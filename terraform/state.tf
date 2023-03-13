
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.3"

  backend "s3" {
    region = "eu-west-2"
  }
}

provider "aws" {
  region = "eu-west-2"
}


data "aws_caller_identity" "current" {}
