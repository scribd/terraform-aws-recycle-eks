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
