from http import HTTPStatus
from uuid import uuid4

from ..lib.write_log import write_log
from .get_access_token import get_access_token
from .make_request import make_get_request

# This will need to be changed if we ever integrate with prod
PDS_FHIR_ENDPOINT = "https://int.api.service.nhs.uk/personal-demographics/FHIR/R4/Patient"


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
    elif response.status_code != HTTPStatus.OK:
        write_log(
            "PDS003",
            {
                "nhs_number": nhs_number,
                "status_code": response.status_code,
                "error": response.json()
            }
        )

    return response.status_code, response.json()
