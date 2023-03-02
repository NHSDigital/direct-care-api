import boto3


def get_ssm_client():
    """Extract to separate function for easy mocking"""
    return boto3.client("ssm", region_name="eu-west-2")


def get_encrypted_ssm_secret(parameter_name):  # pragma: no cover
    """Get an encrypted secret from SSM"""

    ssm_client = get_ssm_client()

    response = ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)
    return response.get("Parameter", {}).get("Value")
