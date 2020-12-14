# defining aws roles and policies for a lambda function

data "aws_iam_policy_document" "lambda-assume-role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}
resource "aws_iam_policy" "lambda_eks_policy" {
  name        = "lambda_eks_policy"
  path        = "/"
  description = "Policy to provide permissions to lambda functions"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "sts:GetCallerIdentity",
                "eks:DescribeCluster",
                "autoscaling:*",
                "ec2:TerminateInstances",
                "ec2:StopInstances"
            ],
            "Effect": "Allow",
            "Resource": "*"
        }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "lambda_eks_policy" {
  role       = aws_iam_role.lambda-exec.name
  policy_arn = aws_iam_policy.lambda_eks_policy.arn
}

resource "aws_iam_role" "lambda-exec" {
  name                 = "${var.name}-lambda-exec-role"
  tags                 = var.tags
  max_session_duration = 43200
  assume_role_policy   = data.aws_iam_policy_document.lambda-assume-role.json
}

resource "aws_iam_role_policy_attachment" "lambda-exec" {
  role       = aws_iam_role.lambda-exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "cluster_AmazonEKSClusterPolicy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.lambda-exec.name
}

resource "aws_iam_role_policy_attachment" "cluster_AmazonEKSServicePolicy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSServicePolicy"
  role       = aws_iam_role.lambda-exec.name
}


# defining aws roles and policies for a step functions state machine

data "aws_iam_policy_document" "sfn-assume-role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["states.${var.aws_region}.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "sfn-exec" {
  name                 = "${var.name}-sfn-exec"
  tags                 = var.tags
  max_session_duration = 43200
  assume_role_policy   = data.aws_iam_policy_document.sfn-assume-role.json
}

data "aws_iam_policy_document" "lambda-invoke" {
  statement {
    actions = [
      "lambda:InvokeFunction"
    ]
    resources = [
      "*",
    ]
  }
}

resource "aws_iam_policy" "lambda-invoke" {
  name   = "${var.name}-lambda-invoke"
  policy = data.aws_iam_policy_document.lambda-invoke.json
}

resource "aws_iam_role_policy_attachment" "lambda-invoke" {
  role       = aws_iam_role.sfn-exec.name
  policy_arn = aws_iam_policy.lambda-invoke.arn
}


resource "kubernetes_cluster_role" "lambda-access" {
  metadata {
    name = "lambda-access"
  }

  rule {
    api_groups = [""]
    resources  = ["nodes", "pods"]
    verbs      = ["get", "list", "watch", "patch"]
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
    name      = "lambda"
    api_group = "rbac.authorization.k8s.io"
  }
}
