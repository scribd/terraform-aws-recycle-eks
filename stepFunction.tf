resource "aws_sfn_state_machine" "sfn_state_machine" {
  name     = "${module.labels.id}-state-function"
  role_arn = aws_iam_role.sfn-exec.arn

  definition = data.template_file.sfn-definition.rendered
}

# step function definition template

data "template_file" "sfn-definition" {
  template = "${file(var.step_function_definition_file)}"
}
