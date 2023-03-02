from time import time
from uuid import uuid4

import jwt
import requests

from .get_ssm_param import get_encrypted_ssm_secret

# These will need to be changed if we ever integrate with prod
KID = "int-1"
OAUTH_ENDPOINT = "https://int.api.service.nhs.uk/oauth2/token"


def create_client_assertion():
    """Create JWT assertion for Oauth request"""

    private_key = get_encrypted_ssm_secret("apim_private_key")
    api_key = get_encrypted_ssm_secret("apim_api_key")

    headers = {"alg": "RS512", "typ": "JWT", "kid": "int-1"}
    payload = {
        "iss": api_key,
        "sub": api_key,
        "aud": OAUTH_ENDPOINT,
        "jti": str(uuid4()),
        "exp": int(time()) + 300,
    }

    return jwt.encode(
        payload, key=private_key, algorithm="RS512", headers=headers
    )


def get_access_token():
    """Return the access token used to retrieve user data"""
    client_assertion = create_client_assertion()
    data = {
        "client_assertion": client_assertion,
        "grant_type": "client_credentials",
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
    }

    token_response = requests.post(
        OAUTH_ENDPOINT,
        data=data,
        headers={"content-type": "application/x-www-form-urlencoded"},
    ).json()

    return token_response.get("access_token")
