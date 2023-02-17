import json
from typing import Dict
import requests

SDS_URL = "https://sandbox.api.service.nhs.uk/spine-directory/FHIR/R4"


def get_structured_url(ods_code):
    ods_code = "comes from pds"
    header = "some header"
    response = requests.get(SDS_URL/{something}/{ods_code}/{something2})
    return json.loads(response.text)


def handler(event, _context) -> Dict:
    """Invokes a lambda"""
    ods_code = event["ods_code"]

    return {
        "statusCode": 200,
        "body": {
            "result": get_structured_url(ods_code),
        },
    }
