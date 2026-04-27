provider "aws" {
  region = var.aws_region
}

terraform {
  backend "s3" {
    bucket         = "base-log-analyzer-tf-state"
    key            = "global/s3/terraform.tfstate"
    region         = "eu-west-1"
    dynamodb_table = "terraform-state-locking"
    encrypt        = true
  }
}
