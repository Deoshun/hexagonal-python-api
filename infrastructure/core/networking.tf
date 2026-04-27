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


# The Load Balancer
resource "aws_lb" "main" {
  name               = "log-analyzer-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = module.vpc.public_subnets
  idle_timeout       = 300
}

# The Target Group (Health check is vital for ECS)
resource "aws_lb_target_group" "app" {
  name        = "log-analyzer-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = module.vpc.vpc_id
  target_type = "ip"

  health_check {
    path                = "/healthz"
    port                = "8000"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
  }
}

# The Listener (External port 80 -> Target Group)
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

resource "aws_cloudfront_distribution" "app_dist" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "CloudFront for Log Analyzer"
  price_class         = "PriceClass_100" # Lowest cost (US/EU/CA)

  origin {
    domain_name = aws_lb.main.dns_name
    origin_id   = "ALB-LogAnalyzer"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only" # ALB is on port 80 for now
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    target_origin_id       = "ALB-LogAnalyzer"
    viewer_protocol_policy = "redirect-to-https" # Force SSL
    allowed_methods        = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods         = ["GET", "HEAD"]

    forwarded_values {
      query_string = true
      headers      = ["Host", "Origin", "Authorization"]
      cookies {
        forward = "all"
      }
    }

    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

output "cloudfront_url" {
  value = aws_cloudfront_distribution.app_dist.domain_name
}
