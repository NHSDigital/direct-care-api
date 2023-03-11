data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = [
      "sts:AssumeRole",
    ]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_role" {
  name               = "lambda_role"
  path               = "/system/"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}



data "aws_iam_policy_document" "lambda_permissions" {
  statement {
    actions = [
      "logs:PutLogEvents",
      "logs:CreateLogStream",
      "logs:CreateLogGroup",
    ]
    resources = [
      "*"
    ]
  }
}

resource "aws_iam_policy" "lambda_permissions" {
  policy = data.aws_iam_policy_document.lambda_permissions.json
}


resource "aws_iam_role_policy_attachment" "lambda_log_access" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_permissions.arn
}


resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/orchestration"
  retention_in_days = 7
}
