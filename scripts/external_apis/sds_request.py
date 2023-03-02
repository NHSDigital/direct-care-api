"""
Script to ping the SDS patient endpoint

Pre-requisites:
    api key at <root>/api_key.txt
    private_key at <root>/int-1.pem
    ods_code

Usage:
    <from root dir>
    python scripts/sds_request.py <ods_code>

To get ods number used the one extracted from PDS integration environment call,
refer to the integration test pack at:
https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir/pds-fhir-api-test-data

"""

import sys
from time import time
from uuid import uuid4
import jwt


import requests

# pylint: disable= line-too-long

def private_key():
    with open("./int-1.pem", "r", encoding="utf-8") as f:
        return f.read()


def api_key():  # TO RESOLVE NotImplementedError(NotImplementedError: Algorithm 'RS512' could not be found.
    with open("./api_key.txt", "r", encoding="utf-8") as f:
        return f.read().strip()


SECRETS_DICT = {
    "oauth_endpoint": "https://int.api.service.nhs.uk/oauth2/token",
    "sds_fhire_endpoint": "https://int.api.service.nhs.uk/spine-directory/FHIR/R4",
    "service_interraction_id": "https://fhir.nhs.uk/Id/nhsServiceInteractionId|urn:nhs:names:services:psis:REPC_IN150016UK05",
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
        timeout=500
    ).json()

    return token_response.get("access_token")


def device_fhir_lookup(ods_code):
    """Send lookup request to SDS FHIR Device Endpoint"""
    x_request_id = str(uuid4())
    token = get_access_token()
    auth = f"Bearer {token}"
    gp_code = f"https://fhir.nhs.uk/Id/ods-organization-code|{ods_code}"
    device_params = {
        "organization": gp_code,
        "identifier": SECRETS_DICT["service_interraction_id"]
    }

    headers = {
        "x-request-id": x_request_id,
        "Authorization": auth,
    }
    endpoint = SECRETS_DICT["sds_fhir_endpoint"]
    device_url = f"{endpoint}/Device"
    response = requests.get(
        device_url,
        headers=headers,
        params=device_params,
        timeout=500
    )
    return response.status_code, response.json()

def extract_nhsMhsPartyKey(body):  # pylint: disable=redefined-outer-name, invalid-name
    """Extracts the nhsPartyKey value
    from the /Device of SDS FHIR API response"""
    entry_key = body["entry"][0]
    if len(entry_key) == 0:
        raise IndexError

    party_key = body["entry"][0]["resource"]["identifier"][1]["value"]  # pylint: disable=redefined-outer-name
    return party_key

def get_sds_endpoint_data(nhsMhsPartyKey):  # pylint: disable=redefined-outer-name, invalid-name
    """Retrieves the whole response from the /Endpoint endpoint"""
    x_request_id = str(uuid4())
    token = get_access_token()
    auth = f"Bearer {token}"
    nhsMhsPartyKey = extract_nhsMhsPartyKey

    service_interraction_party_key = f"https://fhir.nhs.uk/Id/nhsMhsPartyKey|{nhsMhsPartyKey}"

    endpoint_params = {"identifier": [SECRETS_DICT["service_interraction_id"], service_interraction_party_key]}
    headers = {
        "x-request-id": x_request_id,
        "Authorization": auth,
    }
    endpoint = SECRETS_DICT["sds_fhir_endpoint"]
    endpoint_url = f"{endpoint}/Endpoint"
    response = requests.get(
        url=endpoint_url,
        params=endpoint_params,
        headers=headers,
        timeout=500
    )
    return response.status_code, response.json()


if __name__ == "__main__":
    try:
        ods_code = sys.argv[1]  # pylint: disable=invalid-name
        sds_device_data = device_fhir_lookup(ods_code)
        party_key = extract_nhsMhsPartyKey(sds_device_data)
    except IndexError:
        print("ODS code required as command line argument")
        sys.exit(1)

    status, body = get_sds_endpoint_data(nhsMhsPartyKey=party_key)
    print(f"Status code: {status}")
    print(body)
