# terraform-aws-recycle-eks
Example:

```module "recycle-worker-nodes" {
  source = "git::git@github.com:scribd/terraform-aws-recycle-eks.git"
  # version                = "0.0.2alpha"
  name                   = "string"
  tags                   = List of Tags
  vpc_subnet_ids         = List of subnets
  vpc_security_group_ids = [sg-1, sg-2]
  aws_region             = "us-east-2"

}
```
TODO:


1. Stop using anonymous role and find a way to map the role with a proper user

