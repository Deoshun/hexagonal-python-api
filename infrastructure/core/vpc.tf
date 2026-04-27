module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"

  name = "log-analyzer-vpc"
  cidr = var.vpc_cidr

  azs             = ["eu-west-1a", "eu-west-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true # Saves cost for testing
}


resource "aws_vpc_endpoint" "s3" {
  vpc_id       = module.vpc.vpc_id
  service_name = "com.amazonaws.eu-west-1.s3"
  route_table_ids = concat(module.vpc.private_route_table_ids, module.vpc.public_route_table_ids)
}


resource "aws_security_group" "ecs_sg" {
  name        = "log-analyzer-ecs-sg"
  description = "Allow traffic to log analyzer container"
  vpc_id      = module.vpc.vpc_id

  # Ingress: Allow port 8000 for the FastAPI app
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    # For initial testing, we allow CIDR from the VPC. 
    # Change to [var.my_ip] or the ALB SG later for better security.
    cidr_blocks = [var.vpc_cidr] 
  }

  # Egress: Allow all outbound traffic
  # This is required to pull the image from ECR and stream logs from S3
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "log-analyzer-ecs-sg"
  }
}

data "aws_ec2_managed_prefix_list" "cloudfront" {
  name = "com.amazonaws.global.cloudfront.origin-facing"
}

resource "aws_security_group" "alb_sg" {
  name   = "alb-sg"
  vpc_id = module.vpc.vpc_id

  ingress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    # ONLY allow CloudFront IPs
    prefix_list_ids = [data.aws_ec2_managed_prefix_list.cloudfront.id]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Open to the internet
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

