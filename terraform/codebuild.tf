data "aws_iam_policy_document" "codebuild_assume_role_policy" {
  statement {
    actions = [
      "sts:AssumeRole"
    ]
    principals {
      type        = "Service"
      identifiers = ["codebuild.amazonaws.com"]
    }

  }
}

resource "aws_iam_role" "codebuild_role" {
  name               = "codebuild-role"
  assume_role_policy = data.aws_iam_policy_document.codebuild_assume_role_policy.json
}

resource "aws_iam_role_policy_attachment" "codebuild_role_policy" {
  role       = aws_iam_role.codebuild_role.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

resource "aws_codebuild_project" "terraform_plan" {
  name         = "tf-plan"
  service_role = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type = "BUILD_GENERAL1_SMALL"
    image        = "aws/codebuild/standard:5.0"
    type         = "LINUX_CONTAINER"

    environment_variable {
      name  = "ENV"
      value = terraform.workspace
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "terraform/buildspecs/terraform-plan.yml"
  }


}

resource "aws_codebuild_project" "terraform_apply" {

  name         = "tf-apply"
  service_role = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type = "BUILD_GENERAL1_SMALL"
    image        = "aws/codebuild/standard:5.0"
    type         = "LINUX_CONTAINER"

    environment_variable {
      name  = "ENV"
      value = terraform.workspace
    }


  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "terraform/buildspecs/terraform-apply.yml"
  }


}

resource "aws_codebuild_project" "integration-tests" {
  name         = "integration-tests"
  service_role = aws_iam_role.codebuild_role.arn
  depends_on = [
    aws_api_gateway_stage.lambdas_stage
  ]
  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type = "BUILD_GENERAL1_SMALL"
    image        = "aws/codebuild/standard:5.0"
    type         = "LINUX_CONTAINER"

    environment_variable {
      name  = "BASE_URL"
      value = replace(aws_api_gateway_stage.lambdas_stage.invoke_url, "wss://", "https://")
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "terraform/buildspecs/integration-tests.yml"
  }
}
