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

resource "aws_ecr_repository" "app" {
  name                 = "log-analyzer-app"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}

module "log_analyzer" {
  source = "./modules/ecs-app"

  app_name           = "log-analyzer"
  environment        = "stg"
  vpc_id             = module.vpc.vpc_id
  private_subnets    = module.vpc.private_subnets
  public_subnets     = module.vpc.public_subnets
  container_image    = "${aws_ecr_repository.app.repository_url}:${var.image_tag}"
  allowed_s3_buckets = var.allowed_s3_buckets
}
