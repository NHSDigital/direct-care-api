from typing import Dict
import uuid
import json
import requests
from nhs_number import is_valid

SANDBOX_URL = "https://sandbox.api.service.nhs.uk/personal-demographics/FHIR/R4"


def check_nhs_number(nhs_number):
    return is_valid(str(nhs_number))


def get_pds_patient_data(nhs_number):
    """Retirieve JSON Body from PDS API"""
    headers = {"X-Request-ID": str(uuid.uuid4())}
    pds_response =  requests.get(f"{SANDBOX_URL}/Patient/{nhs_number}", headers=headers)
    return json.loads(pds_response.text)


def get_ods_code(nhs_number):
    """Extract ODS Code from PDS Patient Response"""
    return get_pds_patient_data(nhs_number)["generalPractitioner"][0]["identifier"]["value"]


def handler(event, _context) -> Dict:
    """Invoke PDS Lambda"""
    nhs_number = event["nhs_number"]


    return {
        "statusCode": 200,
        "body": {
            "result": get_ods_code(nhs_number),
            "valid_nhs": check_nhs_number(nhs_number)
        },
    }
