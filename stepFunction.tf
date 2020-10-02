resource "aws_sfn_state_machine" "sfn_state_machine" {
  name       = "${module.labels.id}-state-function"
  role_arn   = aws_iam_role.sfn-exec.arn
  tags       = module.labels.tags
  definition = data.template_file.sfn-definition.rendered
}

# step function definition template

data "template_file" "sfn-definition" {
  template = "${file(var.step_function_definition_file)}"
  vars = {
    put-nodes-to-standby-lambda-arn        = "${module.lambda-put-nodes-to-standby.this_lambda_function_arn}"
    check-nodes-forrunning-pods-lambda-arn = "${module.lambda-check-for-pods.this_lambda_function_arn}"
    taint-nodes-lambda-arn                 = "${module.lambda-taint-nodes.this_lambda_function_arn}"
    detach-and-terminate-node-lambda-arn   = "${module.lambda-detach-and-terminate-node.this_lambda_function_arn}"
  }
}
