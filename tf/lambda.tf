resource "aws_lambda_function" "lambda_function" {
  filename         = "./function.zip"
  source_code_hash = filebase64sha256("./function.zip")
  function_name    = "${var.project}-${var.env}"
  role             = aws_iam_role.iam_for_lambda.arn
  handler          = "handlers.lambda_handler"
  description      = var.description
  timeout          = 30
  memory_size      = 256
  runtime          = "python3.11"
  architectures    = ["arm64"]

  tags = {
    Project     = "${var.project}"
    Environment = "${var.env}"
  }

  environment {
    variables = {
      Environment = "${var.env}"
      Project     = "${var.project}"
    }
  }
}

resource "aws_lambda_event_source_mapping" "sqs_mapping" {
  event_source_arn = aws_sqs_queue.sqs_queue_fifo.arn
  function_name    = aws_lambda_function.lambda_function.arn
  depends_on = [
    aws_iam_role_policy.lambda_policy
  ]
}