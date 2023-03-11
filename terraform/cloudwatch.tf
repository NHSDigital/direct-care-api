
data "aws_iam_policy_document" "cloudwatch_assume_role" {
  statement {
    actions = [
      "sts:AssumeRole"
    ]
    principals {
      type        = "Service"
      identifiers = ["apigateway.amazonaws.com"]
    }

  }
}


resource "aws_iam_role" "cloudwatch" {
  name = "api_gateway_cloudwatch_global"

  assume_role_policy = data.aws_iam_policy_document.cloudwatch_assume_role.json
}

data "aws_iam_policy_document" "cloudwatch_policy" {
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:DescribeLogGroups",
      "logs:DescribeLogStreams",
      "logs:PutLogEvents",
      "logs:GetLogEvents",
      "logs:FilterLogEvents"
    ]
    resources = [
      "*",
    ]
  }
}


resource "aws_iam_policy" "cloudwatch_permissions" {
  policy = data.aws_iam_policy_document.cloudwatch_policy.json

}

resource "aws_iam_role_policy_attachment" "cloudwatch_permissions" {

  role       = aws_iam_role.cloudwatch.id
  policy_arn = aws_iam_policy.cloudwatch_permissions.arn

}
