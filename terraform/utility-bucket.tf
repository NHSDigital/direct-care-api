

resource "aws_s3_bucket" "utility_bucket" {
  bucket        = "dcapi-${local.env}-utility-bucket"
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

resource "aws_s3_bucket_acl" "utility_bucket_acl" {
  bucket = resource.aws_s3_bucket.utility_bucket.id
  acl    = "private"
}
