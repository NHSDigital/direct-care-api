

resource "aws_s3_bucket" "utility_bucket" {
  bucket        = "${var.project-name}-${local.env}-utility-bucket"
  force_destroy = true
}

resource "aws_s3_bucket_lifecycle_configuration" "utility_bucket_lifecycle" {
  bucket = resource.aws_s3_bucket.utility_bucket.id

  rule {
    id = "rule-1"
    noncurrent_version_expiration {
      noncurrent_days = 1
    }

    status = "Enabled"
  }
}


resource "aws_s3_bucket_versioning" "utility_bucket_versioning" {
  bucket = resource.aws_s3_bucket.utility_bucket.id
  versioning_configuration {
    status = "Enabled"
  }

}

resource "aws_s3_bucket_ownership_controls" "full_ownership" {
  bucket = resource.aws_s3_bucket.utility_bucket.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}



# If we're on the int environment, allow dev environment to upload the codebase
# as part of the release process to inititate the int pipeline
resource "aws_s3_bucket_policy" "allow_access_from_another_account" {
  count  = local.env == "int2" ? 1 : 0
  bucket = aws_s3_bucket.utility_bucket.id
  policy = data.aws_iam_policy_document.allow_access_from_another_account[0].json
}

data "aws_iam_policy_document" "allow_access_from_another_account" {
  count = local.env == "int2" ? 1 : 0
  statement {
    principals {
      type        = "AWS"
      identifiers = [local.int_account_id]
    }

    actions = [
      "s3:*"
    ]

    resources = [
      aws_s3_bucket.utility_bucket.arn,
      "${aws_s3_bucket.utility_bucket.arn}/*",
    ]
  }
}
