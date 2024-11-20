resource "aws_secretsmanager_secret" "secrets" {
  name = "${var.project}-secrets-${var.env}"

  tags = {
    Project     = "${var.project}"
    Environment = "${var.env}"
  }
}