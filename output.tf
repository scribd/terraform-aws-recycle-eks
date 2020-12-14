output "lambda_exec_arn" {
  description = "ARN for the execution role for lambda"
  value       = aws_iam_role.lambda-exec.arn
}
