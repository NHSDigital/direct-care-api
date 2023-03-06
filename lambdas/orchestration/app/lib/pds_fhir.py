from http import HTTPStatus
from uuid import uuid4

from ..lib.write_log import write_log
from .get_access_token import get_access_token
from .make_request import make_get_request

# This will need to be changed if we ever integrate with prod
PDS_FHIR_ENDPOINT = "https://int.api.service.nhs.uk/personal-demographics/FHIR/R4/Patient"


def extract_ods_code(body):
    """Extract ODS Code from PDS Patient Response"""
    try:
        return body["generalPractitioner"][0]["identifier"]["value"]
    except IndexError:
        return None


def lookup_nhs_number(nhs_number):
    """Send lookup request to PDS FHIR"""

    write_log("PDS001", {"nhs_number": nhs_number})
    x_request_id = str(uuid4())
    token = get_access_token()
    auth = f"Bearer {token}"

    headers = {
        "x-request-id": x_request_id,
        "Authorization": auth,
    }
    endpoint = PDS_FHIR_ENDPOINT
    url = f"{endpoint}/{nhs_number}"
    response = make_get_request(url, headers)

    # PDS FHIR api returns 400 status code if it doesn't find a matching nhs number
    if response.status_code == HTTPStatus.BAD_REQUEST:
        write_log("PDS002", {"nhs_number": nhs_number})
        return (
            None,
            f"PDS FHIR did not find matching record for nhs_number={nhs_number}",
        )

    # Any other non-200 status code means that something has gone wrong with the FHIR API
    if response.status_code != HTTPStatus.OK:
        write_log(
            "PDS003",
            {
                "nhs_number": nhs_number,
                "status_code": response.status_code,
                "error": response.json(),
            },
        )
        return (
            None,
            f"PDS FHIR returned a non-200 status code with status_code={response.status_code}",
        )

    ods_code = extract_ods_code(response.json())

    # Account for the situation where a record has been retrieved
    # but it does not contain and ods code
    if not ods_code:
        write_log("PDS004", {"nhs_number": nhs_number, "record": response.json()})
        return (
            None,
            f"Pds found record for nhs_number={nhs_number} but ODS code not present",
        )

    return ods_code, "Success"
