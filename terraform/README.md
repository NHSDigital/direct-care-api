# Terraform for AWS

## Pipelines

All terraform commands are handled automatically by the various pipelines:

1. On PR open / update - terraform will create a new workspace with a separate state file that creates the resources from scratch for that PR (github actions)
2. On PR close / merge - terraform uses the state file for that PR to destroy all associated resources (github actions)
3. On merge to main - terraform updates the `dev` resources with any changes from the PR (github actions)
4. On release - terraform updates the `int` resources with any changes from the release cut (codepipeline)

## If you need to use terraform commands locally

### Assume the nhs-direct-care-<env> role

The best way to assume into a role is using the python package awsume (which is automatically installed by the `make install-requirements` command)

To use it, you will need to have the following:

In `~/.aws/config`

```
[profile nhs-direct-care-dev]
source_profile = <your aws username>
role_arn = arn:aws:iam::436014718090:role/NHSDAdminRole
mfa_serial = arn:aws:iam::347250048819:mfa/<your aws username>
output = json

[profile nhs-direct-care-int]
source_profile = <your aws username>
role_arn = arn:aws:iam::503308544674:role/NHSDAdminRole
mfa_serial = arn:aws:iam::347250048819:mfa/<your aws username>
output = json
```

In `~/.aws/credentials`
```
[<your username>]
aws_access_key_id = <your access key id>
aws_secret_access_key = <your access key>
```

To create the above access key you will need to sign in to the AWS console, click the dropdown in the top right and then `Security credentials`. Then under `Access keys` click `Create access key` and follow the instructions (make sure you choose an access key for CLI and ignore their warnings). Copy and paste the generated values into the above file.

You will also need to set up MFA if you haven't done so already which is also on the `Security credentials` page.

You should then be able to use command `awsume nhs-direct-care-dev` which will prompt you to enter your MFA token.

Once submitted you will have access to the CLI for one hour until and then you will need to use the `awsume` command again.

To test you've logged in successfully you can use `aws lambda list-functions` and it should return with a list of the lambdas currently on dev


### Init the correct terraform workspace

1. To work directly on the `dev` environment, awsume into the dev environment then use `make DANGER-tf-init env=dev`. As the name implies, this should not be done as standard practice

2. To work directly on the `int` environment, awsume into the dev environment then use `make DANGER-tf-init env=int`. As the name implies, this should not be done as standard practice

3. To work directly on a pull request environment, use `make switch-to-pr-<PR number>`


### Use commands

Use command `make package-lambdas env=<env>` to create the zip files needed for terraform to plan/apply the lambda functions

To see what changes you would be making use `make tf-plan` and to then apply those changes use `make tf-apply`
