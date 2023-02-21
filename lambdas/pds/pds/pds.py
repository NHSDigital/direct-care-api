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
    return requests.get(
        url=f"{SANDBOX_URL}/Patient/{nhs_number}", headers=headers, timeout=600
    )


def get_ods_code(body):
    """Extract ODS Code from PDS Patient Response"""
    return body["generalPractitioner"][0]["identifier"]["value"]


def handler(event, _context) -> Dict:
    """Invoke PDS Lambda"""
    nhs_number = event["nhs_number"]

    is_valid_nhs_number = is_valid(str(nhs_number))
    ods_code = ""
    if is_valid_nhs_number:
        try:
            respone = get_pds_patient_data(nhs_number)
            status_code = respone.status_code
            body = json.loads(respone.text)
            ods_code = get_ods_code(body)
        except requests.exceptions.HTTPError as err:
            status_code = respone.status_code
            print(err)
        except requests.RequestException as err:
            status_code = respone.status_code
            print(err)
        except Exception as err:  # pylint: disable = broad-exception-caught
            status_code = 500
            print(err)
    else:
        status_code = 404

    return {
        "statusCode": status_code,
        "body": {
            "result": ods_code,
            "valid_nhs": is_valid_nhs_number,
        },
    }
