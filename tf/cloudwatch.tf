resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.lambda_function.function_name}"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_metric_filter" "error_log_filter" {
  name           = "${var.project}-${var.env}-error_log_filter"
  pattern        = "ERROR"
  log_group_name = "/aws/lambda/${aws_lambda_function.lambda_function.function_name}"

  metric_transformation {
    name      = "ERROR"
    namespace = "${aws_lambda_function.lambda_function.function_name}"
    value     = "1"
    default_value = 0
  }
}

resource "aws_sns_topic" "notification_topic" {
  name = "${var.project}-${var.env}-alert_topic"
  tags = {
    Project     = "${var.project}"
    Environment = "${var.env}"
    AWSRegion   = "${var.aws_region}"
  }
}

resource "aws_cloudwatch_metric_alarm" "error_log_filter_alarm" {
  alarm_name          = "${var.project}-${var.env}-error_log_filter_alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "ERROR"
  namespace           = "${aws_lambda_function.lambda_function.function_name}"
  period              = "300"
  statistic           = "Sum"
  treat_missing_data  = "ignore"
  threshold           = "1"
  alarm_description   = "Alarm when the error log count exceeds 1"
  alarm_actions       = [aws_sns_topic.notification_topic.arn]
  tags = {
    Project     = "${var.project}"
    Environment = "${var.env}"
    AWSRegion   = "${var.aws_region}"
  }
}

resource "aws_cloudwatch_metric_alarm" "sqs_alarm" {
  alarm_name          = "${var.project}-${var.env}-sqs_message_inflight_alarm"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "1"
  metric_name         = "ApproximateNumberOfMessagesNotVisible"
  namespace           = "AWS/SQS"
  period              = "300"
  statistic           = "Average"
  treat_missing_data  = "notBreaching"
  threshold           = "1"
  alarm_description   = "Alarm when SQS messages visible exceeds 1 for 5 minute"
  alarm_actions       = [aws_sns_topic.notification_topic.arn]
  tags = {
    Project     = "${var.project}"
    Environment = "${var.env}"
    AWSRegion   = "${var.aws_region}"
  }

  dimensions = {
    QueueName = aws_sqs_queue.sqs_queue_fifo.name
  }
}