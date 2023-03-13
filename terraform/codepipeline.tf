data "aws_iam_policy_document" "codepipeline_assume_role_policy" {
  statement {
    actions = [
      "sts:AssumeRole"
    ]
    principals {
      type        = "Service"
      identifiers = ["codepipeline.amazonaws.com"]
    }

  }
}

data "aws_iam_policy_document" "codepipeline_permissions_policy" {
  statement {
    actions = [
      "s3:*",
    ]
    resources = [
      aws_s3_bucket.utility_bucket.arn,
      "${aws_s3_bucket.utility_bucket.arn}/*"
    ]
  }

  statement {
    actions = [
      "codebuild:BatchGetBuilds",
      "codebuild:StartBuild",
      "codebuild:BatchGetBuildBatches",
      "codebuild:StartBuildBatch"
    ]
    effect = "Allow"
    resources = [
      aws_codebuild_project.terraform_plan.arn,
      aws_codebuild_project.terraform_apply.arn,
      aws_codebuild_project.integration-tests.arn,
    ]
  }
}


resource "aws_iam_role" "codepipeline_role" {
  name               = "codepipeline-role-${local.env}"
  assume_role_policy = data.aws_iam_policy_document.codepipeline_assume_role_policy.json
}

resource "aws_iam_policy" "codepipeline_permissions" {
  name   = "codepipeline-permissions"
  policy = data.aws_iam_policy_document.codepipeline_permissions_policy.json
}


resource "aws_iam_role_policy_attachment" "codepipeline_permissions" {
  role       = aws_iam_role.codepipeline_role.name
  policy_arn = aws_iam_policy.codepipeline_permissions.arn
}


resource "aws_codepipeline" "codepipeline_resource" {
  name     = "codepipeline-${local.env}"
  role_arn = aws_iam_role.codepipeline_role.arn

  artifact_store {
    location = aws_s3_bucket.utility_bucket.bucket
    type     = "S3"
  }

  stage {
    name = "Source"
    action {
      category         = "Source"
      name             = "Source"
      owner            = "AWS"
      provider         = "S3"
      version          = "1"
      output_artifacts = ["codeSource"]

      configuration = {
        S3Bucket             = aws_s3_bucket.utility_bucket.bucket
        S3ObjectKey          = "codepipeline-dev/source/${terraform.workspace}-codebase-bundle.zip"
        PollForSourceChanges = true
      }
    }
  }
  stage {
    name = "Plan"

    action {
      run_order        = 1
      name             = "Terraform-Plan"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["codeSource"]
      output_artifacts = ["tfplan"]
      version          = "1"

      configuration = {
        ProjectName = aws_codebuild_project.terraform_plan.name
      }

    }
  }
  stage {
    name = "Deploy"

    action {
      category  = "Approval"
      name      = "Check-Plan-Output-And-Approve"
      owner     = "AWS"
      provider  = "Manual"
      version   = "1"
      run_order = 2
    }

    action {
      run_order        = 3
      name             = "Terraform-Apply"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["codeSource", "tfplan"]
      output_artifacts = []
      version          = "1"

      configuration = {
        ProjectName   = aws_codebuild_project.terraform_apply.name
        PrimarySource = "codeSource"
      }
    }
  }
  stage {
    name = "Test"

    action {
      run_order        = 4
      name             = "Smoketests"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["codeSource"]
      output_artifacts = []
      version          = "1"

      configuration = {
        ProjectName = aws_codebuild_project.integration-tests.name
      }
    }
  }
}
