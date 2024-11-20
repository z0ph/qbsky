resource "aws_secretsmanager_secret" "ACCESS_TOKEN" {
  name = "ACCESS_TOKEN-${var.project}-${var.env}"

  tags = {
    Project     = "${var.project}"
    Environment = "${var.env}"
  }
}