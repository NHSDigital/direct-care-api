from uuid import uuid4

import requests

from .get_access_token import get_access_token

PDS_FHIR_ENDPOINT = "https://int.api.service.nhs.uk/personal-demographics/FHIR/R4/Patient"


def lookup_nhs_number(nhs_number):
    """Send lookup request to PDS FHIR"""
    x_request_id = str(uuid4())
    token = get_access_token()
    auth = f"Bearer {token}"

    headers = {
        "x-request-id": x_request_id,
        "Authorization": auth,
    }
    endpoint = PDS_FHIR_ENDPOINT
    url = f"{endpoint}/{nhs_number}"
    response = requests.get(url, headers=headers)
    return response.status_code, response.json()
