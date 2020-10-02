module "lambda-put-nodes-to-standby" {
  source                        = "terraform-aws-modules/lambda/aws"
  attach_cloudwatch_logs_policy = false
  attach_tracing_policy         = false
  attach_async_event_policy     = false
  attach_policy                 = true
  lambda_role                   = aws_iam_role.lambda-exec.arn
  function_name                 = "hackweek-put-nodes-to-standby"
  description                   = "A lambda function to put an instance to standby"
  handler                       = "putNodesToStandby.lambda_handler"
  runtime                       = "python3.8"
  timeout                       = 180
  create_role                   = false
  source_path                   = "${path.module}/lambdas/putNodesToStandby.py"
  tags                          = module.labels.tags
}

module "lambda-check-for-pods" {
  source                        = "terraform-aws-modules/lambda/aws"
  attach_cloudwatch_logs_policy = false
  attach_tracing_policy         = false
  attach_async_event_policy     = false
  attach_policy                 = true
  lambda_role                   = aws_iam_role.lambda-exec.arn
  create_role                   = false
  function_name                 = "hackweek-check-for-running-pods"
  description                   = "A lambda function to check for running pods in an instance"
  handler                       = "checkNodesForRunningPods.handler"
  runtime                       = "python3.8"
  timeout                       = 180

  source_path = [
    {
      path             = "${path.module}/lambdas/checkNodesForRunningPods.py"
      pip_requirements = false
      # pip_requirements = true  # Will run "pip install" with default requirements.txt
    },
    {
      path             = "${path.module}/awscli-lambda-layer/"
      pip_requirements = false
    }
  ]
  tags = module.labels.tags
}

module "lambda-taint-nodes" {
  source                        = "terraform-aws-modules/lambda/aws"
  attach_cloudwatch_logs_policy = false
  attach_tracing_policy         = false
  attach_async_event_policy     = false
  attach_policy                 = true
  lambda_role                   = aws_iam_role.lambda-exec.arn
  create_role                   = false
  function_name                 = "hackweek-taint-nodes"
  description                   = "A lambda function to ensure no more scheduling on that node"
  handler                       = "taintNodes.handler"
  runtime                       = "python3.8"
  timeout                       = 180

  source_path = [
    {
      path             = "${path.module}/lambdas/taintNodes.py"
      pip_requirements = false
      # pip_requirements = true  # Will run "pip install" with default requirements.txt
    },
    {
      path             = "${path.module}/awscli-lambda-layer/"
      pip_requirements = false
    }
  ]
  tags = module.labels.tags
}

module "lambda-detach-and-terminate-node" {
  source                        = "terraform-aws-modules/lambda/aws"
  attach_cloudwatch_logs_policy = false
  attach_tracing_policy         = false
  attach_async_event_policy     = false
  attach_policy                 = true
  lambda_role                   = aws_iam_role.lambda-exec.arn
  create_role                   = false
  function_name                 = "hackweek-detachand-terminate-node"
  description                   = "A lambda function to detach a node from asg and terminate it"
  handler                       = "detachAndTerminateNode.lambda_handler"
  runtime                       = "python3.8"
  timeout                       = 180
  source_path                   = "${path.module}/lambdas/detachAndTerminateNode.py"
  tags                          = module.labels.tags
}
