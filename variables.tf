variable "aws_region" {
  type        = string
  description = "AWS Region to default resources into"
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
variable "namespace" {
  description = "The namespace against which the pods will be checked"
  type        = string
  default     = "default"
}

variable "runtime_python" {
  description = "The runtime version for python env"
  type        = string
  default     = "python3.8"
}

variable "create_rbac_roles" {
  description = "making the creation of rbac roles optional"
  type        = boolean
  default     = false
}
