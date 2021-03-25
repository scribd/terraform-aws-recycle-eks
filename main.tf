module "lambda-put-nodes-to-standby" {
  source                        = "terraform-aws-modules/lambda/aws"
  version                       = "1.30.0"
  attach_cloudwatch_logs_policy = false
  attach_tracing_policy         = false
  attach_async_event_policy     = false
  attach_policy                 = true
  lambda_role                   = aws_iam_role.lambda-exec.arn
  function_name                 = "${var.name}-put-nodes-to-standby"
  description                   = "A lambda function to put an instance to standby"
  handler                       = "putNodesToStandby.lambda_handler"
  runtime                       = var.runtime_python
  timeout                       = 900
  create_role                   = false
  source_path                   = "${path.module}/lambdas/putNodesToStandby.py"
  tags                          = var.tags
  vpc_subnet_ids                = var.vpc_subnet_ids
  vpc_security_group_ids        = var.vpc_security_group_ids
  attach_network_policy         = true
}

module "lambda-check-for-pods" {
  source                        = "terraform-aws-modules/lambda/aws"
  version                       = "1.30.0"
  attach_cloudwatch_logs_policy = false
  attach_tracing_policy         = false
  attach_async_event_policy     = false
  attach_policy                 = true
  lambda_role                   = aws_iam_role.lambda-exec.arn
  create_role                   = false
  function_name                 = "${var.name}-check-for-running-pods"
  description                   = "A lambda function to check for running pods in an instance"
  handler                       = "checkNodesForRunningPods.handler"
  runtime                       = var.runtime_python
  timeout                       = 60

  source_path = [
    {
      path             = "${path.module}/lambdas/checkNodesForRunningPods.py"
      pip_requirements = false
    },
    {
      path             = "${path.module}/lambdas/requirements.txt"
      pip_requirements = true
    }
  ]
  tags                   = var.tags
  vpc_subnet_ids         = var.vpc_subnet_ids
  vpc_security_group_ids = var.vpc_security_group_ids
  attach_network_policy  = true
}

module "lambda-taint-nodes" {
  source                        = "terraform-aws-modules/lambda/aws"
  version                       = "1.30.0"
  attach_cloudwatch_logs_policy = false
  attach_tracing_policy         = false
  attach_async_event_policy     = false
  attach_policy                 = true
  lambda_role                   = aws_iam_role.lambda-exec.arn
  create_role                   = false
  function_name                 = "${var.name}-taint-nodes"
  description                   = "A lambda function to ensure no more scheduling on that node"
  handler                       = "taintNodes.handler"
  runtime                       = var.runtime_python
  timeout                       = 60

  source_path = [
    {
      path             = "${path.module}/lambdas/taintNodes.py"
      pip_requirements = false
    },
    {
      path             = "${path.module}/lambdas/requirements.txt"
      pip_requirements = true
    }
  ]
  tags                   = var.tags
  vpc_subnet_ids         = var.vpc_subnet_ids
  vpc_security_group_ids = var.vpc_security_group_ids
  attach_network_policy  = true
}

module "lambda-detach-and-terminate-node" {
  source                        = "terraform-aws-modules/lambda/aws"
  version                       = "1.30.0"
  attach_cloudwatch_logs_policy = false
  attach_tracing_policy         = false
  attach_async_event_policy     = false
  attach_policy                 = true
  lambda_role                   = aws_iam_role.lambda-exec.arn
  create_role                   = false
  function_name                 = "${var.name}-detachand-terminate-node"
  description                   = "A lambda function to detach a node from asg and terminate it"
  handler                       = "detachAndTerminateNode.lambda_handler"
  runtime                       = var.runtime_python
  timeout                       = 60
  source_path                   = "${path.module}/lambdas/detachAndTerminateNode.py"
  tags                          = var.tags
  vpc_subnet_ids                = var.vpc_subnet_ids
  vpc_security_group_ids        = var.vpc_security_group_ids
  attach_network_policy         = true
}
