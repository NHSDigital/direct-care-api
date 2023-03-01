"""
Script to ping the PDS patient endpoint

Pre-requisites:
    api key at <root>/api_key.txt
    private_key at <root>/int-1.pem

Usage:
    <from root dir>
    python scripts/pds_request <nhs_number>

To get nhs numbers available in the PDS integration environment,
refer to the integration test pack at:
https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir/pds-fhir-api-test-data

"""

import jwt
import requests
from uuid import uuid4
from time import time
import sys


def private_key():
    with open("./int-1.pem", "r", encoding="utf-8") as f:
        return f.read()


def api_key():
    with open("./api_key.txt", "r", encoding="utf-8") as f:
        return f.read().strip()


SECRETS_DICT = {
    "oauth_endpoint": "https://int.api.service.nhs.uk/oauth2/token",
    "pds_fhir_endpoint": "https://int.api.service.nhs.uk/personal-demographics/FHIR/R4/Patient",
    "api_key": api_key(),
    "private_key": private_key(),
    "kid": "int-1",
}


def create_client_assertion():
    """Create JWT assertion for Oauth request"""
    headers = {"alg": "RS512", "typ": "JWT", "kid": SECRETS_DICT["kid"]}
    payload = {
        "iss": SECRETS_DICT["api_key"],
        "sub": SECRETS_DICT["api_key"],
        "aud": SECRETS_DICT["oauth_endpoint"],
        "jti": str(uuid4()),
        "exp": int(time()) + 300,
    }

    print(payload)

    return jwt.encode(
        payload, key=SECRETS_DICT["private_key"], algorithm="RS512", headers=headers
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
        SECRETS_DICT["oauth_endpoint"],
        data=data,
        headers={"content-type": "application/x-www-form-urlencoded"},
    ).json()
    print(token_response)
    return token_response.get("access_token")


def pds_fhir_lookup(nhs_number):
    """Send lookup request to PDS FHIR"""
    x_request_id = str(uuid4())
    token = get_access_token()
    auth = f"Bearer {token}"

    headers = {
        "x-request-id": x_request_id,
        "Authorization": auth,
    }
    endpoint = SECRETS_DICT["pds_fhir_endpoint"]
    url = f"{endpoint}/{nhs_number}"
    response = requests.get(url, headers=headers)
    return response.status_code, response.json()


if __name__ == "__main__":
    try:
        nhs_number = sys.argv[1]
    except IndexError:
        print("NHS number required as command line argument")
        exit(1)

    status, body = pds_fhir_lookup(nhs_number)
    print(f"Status code: {status}")
    print(body)
