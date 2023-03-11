data "aws_s3_object" "packages_zip" {
  bucket = "dcapi-${local.env}-utility-bucket"
  key    = "shared_layer/python.zip"
}

resource "aws_lambda_layer_version" "python-packages" {
  s3_bucket           = data.aws_s3_object.packages_zip.bucket
  s3_key              = data.aws_s3_object.packages_zip.key
  layer_name          = "python-packages"
  s3_object_version   = data.aws_s3_object.packages_zip.version_id
  compatible_runtimes = ["python3.9"]
}


resource "aws_lambda_function" "lambda" {
  filename      = "../build/lambda_archives/orchestration.zip"
  function_name = "orchestration-lambda-${local.env}"
  role          = aws_iam_role.lambda_role.arn
  handler       = "app.orchestration_handler.main"
  timeout       = 30
  memory_size   = 1024

  runtime = "python3.9"

  source_code_hash = filebase64sha256("../build/lambda_archives/orchestration.zip")
  layers           = [aws_lambda_layer_version.python-packages.arn]
}


resource "aws_lambda_permission" "lambda_permission" {
  depends_on = [
    aws_api_gateway_rest_api.api_gateway,
    aws_lambda_function.lambda
  ]
  statement_id  = "AllowExecutionFromApi"
  action        = "lambda:InvokeFunction"
  function_name = "orchestration-lambda-${local.env}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api_gateway.execution_arn}/*/*"
}
