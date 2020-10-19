variable "aws_region" {
  type        = string
  default     = "us-east-2"
  description = "AWS Region to default resources into"
}

variable "network_master_vpc" {
  type        = string
  description = "VPC from network master to deploy the stack into"
  default     = "migration"
}

variable "prefix" {
  type        = string
  description = "Prefix for key AWS resources to use, such as the developers user name"
}

variable "owner" {
  type        = string
  description = "Tag to use for helping map owners to their resources"
}

variable "department" {
  type        = string
  description = "Tag to use for helping map department to their resources"
}

variable "env" {
  type        = string
  description = "Environment prefix"
}

variable "instance_type" {
  type        = string
  default     = "m4.large"
  description = "Instance type for the worker nodes"
}

# state machine variables

variable "step_function_definition_file" {
  default = "step-function.json"
}

variable "step_function_name" {
  default = "StepFunctionWorkflow"
}

variable "cluster_name" {
  type        = string
  description = "EKS cluster name"
  default     = "hackweek-2020-local-eks-cluster"
}

# variable "map_roles" {
#   description = "Additional IAM roles to add to the aws-auth configmap."
#   default = [
#     {
#       groups = ["system:anonymous"]
#     },
#   ]
# }
