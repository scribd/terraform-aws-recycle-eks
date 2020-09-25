module "labels" {
  source    = "git::https://github.com/cloudposse/terraform-null-label.git?ref=0.14.1"
  namespace = var.prefix
  stage     = var.env
  name      = "eks-cluster"
  delimiter = "-"
  tags = {
    terraform   = "true"
    Workspace   = "${terraform.workspace}"
    owner       = "${var.owner}"
    source_repo = "https://github.com/scribd/terraform-aws-recycle-eks"
    department  = "${var.department}"
    project     = "hackweek-2020"
  }
}
