# Terraform for AWS

## Manual steps to create the necessary terraform resources

This only needs to be done once but the process is here for reference

`make create-terraform-state-resources-[env]`

## Assuming the nhs-direct-care-dev role locally

The best way to assume into a role is using the python package awsume (which is automatically installed by the `make install-requirements` command)

To use it, you will need to have the following:

In `~/.aws/config`

```
[profile nhs-direct-care-dev]
source_profile = <your aws username>
role_arn = arn:aws:iam::436014718090:role/NHSDAdminRole
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
