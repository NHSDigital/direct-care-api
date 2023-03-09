from http import HTTPStatus
from uuid import uuid4

from scripts.external_apis.sds_request import api_key

from .get_dict_value import get_dict_value
from .make_request import make_get_request

# pylint: disable=line-too-long

# This will need to be changed if we ever integrate with prod
SDS_FHIR_ENDPOINT = "https://int.api.service.nhs.uk/spine-directory/FHIR/R4"
SERVICE_INTERACTION_ID = "https://fhir.nhs.uk/Id/nhsServiceInteractionId|urn:nhs:names:services:gpconnect:fhir:operation:gpc.getstructuredrecord-1"
ORG_CODE_BASE = "https://fhir.nhs.uk/Id/ods-organization-code|"

def extract_address(body):  # pylint: disable=redefined-outer-name, invalid-name # noqa: E302
    """Extracts the address value from the /Endpoint of SDS FHIR API response"""
    entry_key = body["entry"][0]
    if len(entry_key) == 0:
        raise IndexError

    address = body["entry"][0]["resource"]["address"]
    return address


def device_fhir_lookup(ods_code, write_log):
    """Send lookup request to SDS FHIR Device Endpoint"""

    write_log("SDS001", {"ods_code": ods_code})
    x_request_id = str(uuid4())
    gp_code = f"{ORG_CODE_BASE}{ods_code}"
    device_params = {"organization": gp_code, "identifier": [SERVICE_INTERACTION_ID]}

    headers = {
        "x-request-id": x_request_id,
        "apikey": api_key(),
    }
    endpoint = SDS_FHIR_ENDPOINT
    device_url = f"{endpoint}/Device"
    response = make_get_request(device_url, device_params, headers)

    # FHIR api returns 400 status code if it doesn't find a matching ODS_CODE
    if response.status_code == HTTPStatus.BAD_REQUEST:
        write_log("SDS002", {"ods_code": ods_code})
        return (
            None,
            f"SDS FHIR did not find matching record for ods_code={ods_code}",
        )
    if response.status_code != HTTPStatus.OK:
        write_log(
            "SDS003",
            {
                "ods_code": ods_code,
                "status_code": response.status_code,
                "error": response.json(),
            },
        )
        return (
            None,
            f"SDS FHIR returned a non-200 status code with status_code={response.status_code}",
        )

    nhsMhsPartyKey = get_dict_value(response.json(), "entry/0/resource/identifier/1/value")  # pylint: disable=invalid-name
    asid = get_dict_value(response.json(), "entry/0/resource/identifier/0/value")

    # Account for the situation where a record has been retrieved
    # but it does not contain and ods code
    if not nhsMhsPartyKey:
        write_log("SDS004", {"ods_code": ods_code, "record": response.json()})
        return (
            None,
            f"SDS FHIR found record for ods_code={ods_code} but party key not present in record.",
        )
    elif not asid:
        write_log("SDS005", {"ods_code": ods_code, "record": response.json()})
        return (
            None,
            f"SDS FHIR found record for ods_code={ods_code} but ASID number not present in record.",
        )

    return nhsMhsPartyKey, asid, "Success"
