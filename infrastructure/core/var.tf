variable "allowed_s3_buckets" {
  type        = list(string)
  default     = ["my-log-bucket"] 
}

variable "vpc_cidr" {
  default = "10.0.0.0/16"
}

variable "aws_region" {
  type    = string
  default = "eu-west-1"
}

variable "image_tag" {
  type    = string
  default = "latest"
}
