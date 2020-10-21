variable "aws_region" {
  type        = string
  description = "AWS Region to default resources into"
}

variable "cluster_name" {
  type        = string
  description = "EKS cluster name"
}

variable "name" {
  type        = string
  description = "lamda identifiers"
}

variable "tags" {
  description = "A map of tags to assign to resources."
  type        = map(string)
  default     = {}
}

variable "vpc_subnet_ids" {
  description = "List of subnet ids when Lambda Function should run in the VPC. Usually private or intra subnets."
  type        = list(string)
  default     = null
}

variable "vpc_security_group_ids" {
  description = "List of security group ids when Lambda Function should run in the VPC."
  type        = list(string)
  default     = null
}
