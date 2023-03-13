"""
Script to ping the SDS patient endpoint

Usage:
    <from root dir>
    python scripts/sds_request.py B82617

To get ods number used the one extracted from PDS integration environment call,
refer to the integration test pack at:
https://digital.nhs.uk/developer/api-catalogue/spine-directory-service-fhir

"""

import sys
from uuid import uuid4

import requests


def api_key():  # noqa: E302
    with open("./api_key.txt", "r", encoding="utf-8") as f:  # pylint: disable= invalid-name
        return f.read().strip()


SDS_FHIR_ENDPOINT = "https://int.api.service.nhs.uk/spine-directory/FHIR/R4"
SERVICE_INTERACTION_ID = "https://fhir.nhs.uk/Id/nhsServiceInteractionId|urn:nhs:names:services:gpconnect:fhir:operation:gpc.getstructuredrecord-1"


def device_fhir_lookup(ods_code):   # pylint: disable=redefined-outer-name
    """Send lookup request to SDS FHIR Device Endpoint"""
    x_request_id = str(uuid4())
    gp_code = f"https://fhir.nhs.uk/Id/ods-organization-code|{ods_code}"
    device_params = {"organization": gp_code, "identifier": [SERVICE_INTERACTION_ID]}

    headers = {
        "x-request-id": x_request_id,
        "apikey": api_key(),
    }
    endpoint = SDS_FHIR_ENDPOINT
    device_url = f"{endpoint}/Device"
    response = requests.get(
        url=device_url, params=device_params, headers=headers, timeout=500
    )
    return response.status_code, response.json()

def extract_nhsMhsPartyKey(body):  # pylint: disable=redefined-outer-name, invalid-name # noqa: E302
    """Extracts the nhsPartyKey value
    from the /Device of SDS FHIR API response"""
    entry_key = body["entry"][0]
    if len(entry_key) == 0:
        raise IndexError

    party_key = body["entry"][0]["resource"]["identifier"][1][
        "value"
    ]  # pylint: disable=redefined-outer-name
    return party_key

def extract_asid(body):  # pylint: disable=redefined-outer-name, invalid-name # noqa: E302
    """Extracts the ASID value from the /Device of SDS FHIR API response"""
    entry_key = body["entry"][0]
    if len(entry_key) == 0:
        raise IndexError

    asid_number = body["entry"][0]["resource"]["identifier"][0]["value"]
    return asid_number

def get_sds_endpoint_data(nhsMhsPartyKey):  # pylint: disable=redefined-outer-name, invalid-name # noqa: E302
    """Retrieves the whole response from the /Endpoint endpoint"""
    x_request_id = str(uuid4())

    service_interraction_party_key = (
        f"https://fhir.nhs.uk/Id/nhsMhsPartyKey|{nhsMhsPartyKey}"
    )

    endpoint_params = {
        "identifier": [SERVICE_INTERACTION_ID, service_interraction_party_key]
    }
    headers = {
        "x-request-id": x_request_id,
        "apikey": api_key(),
    }
    endpoint = SDS_FHIR_ENDPOINT
    endpoint_url = f"{endpoint}/Endpoint"
    response = requests.get(
        url=endpoint_url, params=endpoint_params, headers=headers, timeout=500
    )
    print(response.json())
    return response.status_code, response.json()

def extract_address(body):  # pylint: disable=redefined-outer-name, invalid-name # noqa: E302
    """Extracts the address value from the /Endpoint of SDS FHIR API response"""
    entry_key = body["entry"][0]
    if len(entry_key) == 0:
        raise IndexError

    address = body["entry"][0]["resource"]["address"]
    return address


if __name__ == "__main__":
    try:
        ods_code = sys.argv[1]  # pylint: disable=invalid-name # noqa: E302
        status_code, sds_device_data = device_fhir_lookup(ods_code)
        party_key = extract_nhsMhsPartyKey(sds_device_data)
    except IndexError:
        print("ODS code required as command line argument")
        sys.exit(1)

    status, body = get_sds_endpoint_data(nhsMhsPartyKey=party_key)
    print(f"ASID: {extract_asid(sds_device_data)}")
    print(f"Address: {extract_address(body)}")
