data "aws_eks_cluster" "cluster" {
  name = module.eks-cluster.cluster_id
}

data "aws_eks_cluster_auth" "cluster" {
  name = module.eks-cluster.cluster_id
}

provider "kubernetes" {
  host                   = data.aws_eks_cluster.cluster.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority.0.data)
  token                  = data.aws_eks_cluster_auth.cluster.token
  load_config_file       = false
  version                = "~> 1.9"
}

module "eks-cluster" {
  source          = "terraform-aws-modules/eks/aws"
  cluster_name    = module.labels.id
  cluster_version = "1.17"
  subnets         = local.private_subnets.subnet_ids
  vpc_id          = local.vpc_id
  tags            = module.labels.tags
  worker_groups = [
    {
      instance_type        = var.instance_type
      asg_desired_capacity = 2
      asg_max_size         = 5
      asg_min_size         = 2
    }
  ]
}


resource "kubernetes_cluster_role" "lambda-access" {
  metadata {
    name = "lambda-access"
  }

  rule {
    api_groups = [""]
    resources  = ["nodes", "pods"]
    verbs      = ["get", "list", "watch"]
  }
}

resource "kubernetes_cluster_role_binding" "lambda-user-role-binding" {
  metadata {
    name = "lambda-user-role-binding"
  }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "lambda-access"
  }
  subject {
    kind      = "User"
    name      = "system:anonymous"
    api_group = "rbac.authorization.k8s.io"
    namespace = "kube-system"
  }
}
