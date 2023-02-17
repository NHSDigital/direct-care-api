from typing import Dict
import uuid
import json
import requests
from nhs_number import is_valid

SANDBOX_URL = "https://sandbox.api.service.nhs.uk/personal-demographics/FHIR/R4"


def check_nhs_number(nhs_number):
    """Check NHS Number"""
    return is_valid(str(nhs_number))


def get_pds_patient_data(nhs_number):
    """Retirieve JSON Body from PDS API"""
    headers = {"X-Request-ID": str(uuid.uuid4())}

    return requests.get(f"{SANDBOX_URL}/Patient/{nhs_number}", headers=headers)


def get_ods_code(body):
    """Extract ODS Code from PDS Patient Response"""
    return body["generalPractitioner"][0]["identifier"]["value"]


def handler(event, _context) -> Dict:
    """Invoke PDS Lambda"""
    nhs_number = event["nhs_number"]

    is_valid_nhs_number = is_valid(str(nhs_number))
    if is_valid_nhs_number:
        respone = get_pds_patient_data(nhs_number)

        status_code = respone.status_code

        body = json.loads(respone.text)
        ods_code = get_ods_code(body)

    else:
        status_code = 404
        ods_code = ""

    return {
        "statusCode": status_code,
        "body": {
            "result": ods_code,
            "valid_nhs": is_valid_nhs_number,
        },
    }
