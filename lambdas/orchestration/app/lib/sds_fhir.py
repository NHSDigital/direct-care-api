from http import HTTPStatus
from uuid import uuid4

from scripts.external_apis.sds_request import api_key

from ..lib.write_log import write_log
from .make_request import make_get_request

# pylint: disable=line-too-long

# This will need to be changed if we ever integrate with prod
SDS_FHIR_ENDPOINT = "https://int.api.service.nhs.uk/spine-directory/FHIR/R4"
SERVICE_INTERACTION_ID = "https://fhir.nhs.uk/Id/nhsServiceInteractionId|urn:nhs:names:services:psis:REPC_IN150016UK05"
ORG_CODE_BASE = "https://fhir.nhs.uk/Id/ods-organization-code|"

def extract_nhsMhsPartyKey(body):  # pylint: disable=redefined-outer-name, invalid-name  # noqa: E302
    """Extracts the nhsPartyKey value
    from the /Device of SDS FHIR API response"""
    entry_key = body["entry"][0]
    if len(entry_key) == 0:
        raise IndexError

    party_key = body["entry"][0]["resource"]["identifier"][1]["value"]  # pylint: disable=redefined-outer-name
    return party_key

def extract_asid(body):  # pylint: disable=redefined-outer-name, invalid-name # noqa: E302
    """Extracts the ASID value from the /Device of SDS FHIR API response"""
    entry_key = body["entry"][0]
    if len(entry_key) == 0:
        raise IndexError

    asid_number = body["entry"][0]["resource"]["identifier"][0]["value"]
    return asid_number

def extract_address(body):  # pylint: disable=redefined-outer-name, invalid-name # noqa: E302
    """Extracts the address value from the /Endpoint of SDS FHIR API response"""
    entry_key = body["entry"][0]
    if len(entry_key) == 0:
        raise IndexError

    address = body["entry"][0]["resource"]["address"]
    return address


def get_device_data(ods_code):
    """Send lookup request to SDS FHIR Device Endpoint"""

    write_log("SDS001", {"ods_code": ods_code})  # TO DO
    x_request_id = str(uuid4())
    gp_code = f"{ORG_CODE_BASE}{ods_code}"
    device_params = {
        "organization": gp_code,
        "identifier": [SERVICE_INTERACTION_ID]
    }

    headers = {
        "x-request-id": x_request_id,
        "apikey": api_key(),
    }
    endpoint = SDS_FHIR_ENDPOINT
    device_url = f"{endpoint}/Device"
    response = make_get_request(device_url, device_params, headers)

    # FHIR api returns 400 status code if it doesn't find a matching ODS_CODE
    if response.status_code == HTTPStatus.BAD_REQUEST:
        # write_log("PDS002", {"nhs_number": nhs_number})
        return (
            None
        )
