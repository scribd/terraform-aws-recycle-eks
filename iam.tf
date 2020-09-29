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

resource "aws_iam_role" "lambda-exec" {
  name                 = "${module.labels.id}-lambda-exec-role"
  max_session_duration = 43200
  assume_role_policy   = data.aws_iam_policy_document.lambda-assume-role.json
}

resource "aws_iam_role_policy_attachment" "lambda-exec" {
  role       = aws_iam_role.lambda-exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
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
