from typing import Dict

SDS_URL = "https://sandbox.api.service.nhs.uk/spine-directory/FHIR/R4"

def handler(event, _context) -> Dict:
    """Invokes a lambda"""
    osd_code = event["ods_code"]

    return {
        "statusCode": 200,
        "body": {
            "result": a_func(ods_code),
        },
    }
