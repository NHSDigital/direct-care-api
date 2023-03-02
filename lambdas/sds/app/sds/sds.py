import uuid
from typing import Dict
import requests as r
from shared.logger import app_logger

# pylint: disable= line-too-long, invalid-name, broad-exception-caught

BASE_URL = "https://sandbox.api.service.nhs.uk/spine-directory/FHIR/R4"
DEVICE_URL = f"{BASE_URL}/Device"
ENDPOINT_URL = f"{BASE_URL}/Endpoint"

SERVICE_INTERACTION_ID_STRUCTURED = "https://fhir.nhs.uk/Id/nhsServiceInteractionId|urn:nhs:names:services:psis:REPC_IN150016UK05" # this is for sandbox purposes it will be replaced with the official one
API_KEY = "123" # this is for sandbox purposes it will be replaced with the official one

def get_sds_device_data(ods_code):
    """Retrieves the whole response from the /Device endpoint"""

    ORG = f"https://fhir.nhs.uk/Id/ods-organization-code|{ods_code}"
    device_params = {"organization": ORG, "identifier": [SERVICE_INTERACTION_ID_STRUCTURED]}
    device_headers = {"X-Correlation-Id": uuid.uuid4(), "apikey": API_KEY} # API reference doesn't specify uuid as a str

    device_req = r.get(url=DEVICE_URL,
        params=device_params,
        headers=device_headers,
        timeout=500)
    device_req.raise_for_status()
    resp_json = device_req.json()

    return resp_json

def extract_nhsMhsPartyKey(body):
    """Extracts the nhsPartyKey value from the /Device of SDS FHIR API response"""
    entry_key = body["entry"][0]
    if len(entry_key)==0:
        raise IndexError

    party_key = body["entry"][0]["resource"]["identifier"][1]["value"]
    return party_key


def extract_asid(body):
    """Extracts the ASID value from the /Device of SDS FHIR API response"""
    entry_key = body["entry"][0]
    if len(entry_key)==0:
        raise IndexError

    asid_number = body["entry"][0]["resource"]["identifier"][0]["value"]
    return asid_number

def get_sds_endpoint_data(nhsMhsPartyKey):
    """Retrieves the whole response from the /Endpoint endpoint"""
    nhsMhsPartyKey = extract_nhsMhsPartyKey

    SERVICE_INTERACTION_ID_PARTY_KEY = f"https://fhir.nhs.uk/Id/nhsMhsPartyKey|{nhsMhsPartyKey}"

    device_params = {"identifier": [SERVICE_INTERACTION_ID_STRUCTURED, SERVICE_INTERACTION_ID_PARTY_KEY]}
    device_headers = {"X-Correlation-Id": uuid.uuid4(), "apikey": API_KEY} # API reference doesn't specify uuid as a str

    endpoint_req = r.get(url=ENDPOINT_URL,
                params=device_params,
                headers=device_headers, timeout=500)
    return endpoint_req.json()


def extract_address(body):
    """Extracts the address value from the /Endpoint of SDS FHIR API response"""
    entry_key = body["entry"][0]
    if len(entry_key)==0:
        raise IndexError

    address = body["entry"][0]["resource"]["address"]
    return address

def handler(event, _context) -> Dict:
    """
    Invokes a lambda
    """

    status_code = 200
    result = ""
    try:
        ods_code = event["ods_code"]
        sds_device_data = get_sds_device_data(ods_code)
        party_key = extract_nhsMhsPartyKey(sds_device_data)
        sds_endpoint_data = get_sds_endpoint_data(nhsMhsPartyKey=party_key)
        result = extract_address(sds_endpoint_data)
    except Exception:
        status_code = 500
        app_logger.exception()

    return {
        "statusCode": status_code,
        "body": {
            "result": result
        },
    }
