data "aws_s3_object" "packages_zip" {
  bucket = "dcapi-dev-pipeline-bucket"
  key    = "python.zip"
}

resource "aws_lambda_layer_version" "python-packages" {
  s3_bucket         = data.aws_s3_object.packages_zip.bucket
  s3_key            = data.aws_s3_object.packages_zip.key
  layer_name        = "python-packages"
  s3_object_version = data.aws_s3_object.packages_zip.version_id
}


resource "aws_lambda_function" "lambda" {
  filename      = "../build/lambda_archives/orchestration.zip"
  function_name = "orchestration_lambda-${local.env}"
  role          = aws_iam_role.lambda_role.arn
  handler       = "app.orchestration_handler.main"
  timeout       = 30
  memory_size   = 1024

  runtime = "python3.9"

  source_code_hash = filebase64sha256("../build/lambda_archives/orchestration.zip")
  layers           = [aws_lambda_layer_version.python-packages.arn]
}
