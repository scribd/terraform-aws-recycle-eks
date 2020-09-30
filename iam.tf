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
  name        = "test_policy"
  path        = "/"
  description = "My test policy"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "sts:GetCallerIdentity",
                "eks:DescribeCluster"
            ],
            "Effect": "Allow",
            "Resource": "*"
        }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "llambda_eks_policy" {
  role       = aws_iam_role.lambda-exec.name
  policy_arn = aws_iam_policy.lambda_eks_policy.arn
}

resource "aws_iam_role" "lambda-exec" {
  name                 = "${module.labels.id}-lambda-exec-role"
  tags                 = module.labels.tags
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
  name                 = "${module.labels.id}-sfn-exec"
  tags                 = module.labels.tags
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
  name   = "${module.labels.id}-lambda-invoke"
  policy = data.aws_iam_policy_document.lambda-invoke.json
}

resource "aws_iam_role_policy_attachment" "lambda-invoke" {
  role       = aws_iam_role.sfn-exec.name
  policy_arn = aws_iam_policy.lambda-invoke.arn
}
