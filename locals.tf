data "aws_caller_identity" "current" {}
locals {
  #network_master_vpcs = data.terraform_remote_state.network_master.outputs.shared_vpcs
  network_master_vpcs = {
    # These values are correct for the "dev" shared VPC and captured from here
    #   https://git.lo/terraform/terraform-aws-networking/blob/master/subnets.json
    "migration" = {
      "private_subnets" = {
        "subnet_cidrs" = [
          "10.226.0.0/19",
          "10.226.32.0/19", "10.226.64.0/19"
        ],
        "subnet_ids" = [
          "subnet-0f06ea029e6bb0899",
          "subnet-0581c47e7b421b3ae",
          "subnet-05fe8fa6adcc7ab4a"
        ]
      },
      "public_subnets" : {
        "subnet_cidrs" : [
          "10.226.128.0/20",
          "10.226.144.0/20",
          "10.226.160.0/20"
        ],
        "subnet_ids" : [
          "subnet-0bcf5784749a8b53d",
          "subnet-06d49badbd1fc05b2",
          "subnet-0e616285ea41203b9"
        ]
      },
      "vpc_id" = "vpc-03e21b0ca5340c75d"
    }
  }

  vpc = local.network_master_vpcs[var.network_master_vpc]

  vpc_id          = local.vpc.vpc_id
  private_subnets = local.vpc.private_subnets
  public_subnets  = local.vpc.public_subnets

  # eventually, we will move these to shared remote state -
  # https://scribdjira.atlassian.net/browse/CPLAT-626
  vpn_cidrs = [
    "10.95.61.0/24",
  ]
  devkube_cidrs = [
    "10.226.0.0/16"
  ]
}
