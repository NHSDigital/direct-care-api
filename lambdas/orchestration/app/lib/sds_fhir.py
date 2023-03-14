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


def device_fhir_lookup(ods_code, write_log):  # pylint: disable=redefined-outer-name
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
    response = make_get_request(device_url, headers, device_params)

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
    nhsMhsPartyKey = get_dict_value(
        response.json(), "/entry/0/resource/identifier/1/value"
    )  # pylint: disable=invalid-name
    asid = get_dict_value(response.json(), "/entry/0/resource/identifier/0/value")

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

    return nhsMhsPartyKey, asid


def get_sds_endpoint_data(
    nhsMhsPartyKey, write_log
):  # pylint: disable=redefined-outer-name, invalid-name # noqa: E302
    """Retrieves the whole response from the /Endpoint endpoint"""
    x_request_id = str(uuid4())

    service_interraction_party_key = f"https://fhir.nhs.uk/Id/nhsMhsPartyKey|{nhsMhsPartyKey}"

    endpoint_params = {"identifier": [SERVICE_INTERACTION_ID, service_interraction_party_key]}
    headers = {
        "x-request-id": x_request_id,
        "apikey": api_key(),
    }
    endpoint = SDS_FHIR_ENDPOINT
    endpoint_url = f"{endpoint}/Endpoint"
    response = make_get_request(endpoint_url, headers, endpoint_params)

    # FHIR api returns 400 status code if it doesn't find a matching party key
    if response.status_code == HTTPStatus.BAD_REQUEST:
        write_log("SDS007", nhsMhsPartyKey={nhsMhsPartyKey})
        return (
            None,
            f"SDS FHIR did not find matching record for nhsMhsPartyKey={nhsMhsPartyKey}",
        )
    if response.status_code != HTTPStatus.OK:
        write_log(
            "SDS003",
            {
                "party_key": nhsMhsPartyKey,
                "status_code": response.status_code,
                "error": response.json(),
            },
        )
        return (
            None,
            f"SDS FHIR returned a non-200 status code with status_code={response.status_code}",
        )

    address = get_dict_value(
        response.json(), "entry/0/resource/address"
    )  # pylint: disable=invalid-name

    # Account for the situation where a record has been retrieved
    # but it does not contain address
    if not address:
        write_log("SDS006", {"party_key": nhsMhsPartyKey, "record": response.json()})
        return (
            None,
            f"SDS FHIR found record for nhsMhsPartyKey={nhsMhsPartyKey} but address not present in record.",
        )

    return address, "Success"


def sds_request(ods_code, write_log):
    party_key, asid = device_fhir_lookup(ods_code, write_log=write_log)
    address, message = get_sds_endpoint_data(party_key, write_log=write_log)
    return asid, address, message
