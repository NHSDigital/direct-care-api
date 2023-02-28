from typing import Dict
import requests

BASE_URL = "https://sandbox.api.service.nhs.uk/spine-directory/FHIR/R4"

def my_requests():
    headers = {"Content-Type": "application/fhir+json ",
                "Accept": "application/fhir+json "}
    method = "get"
    data = {}
    response = requests.request(method, BASE_URL, json=data, headers=headers)
    return response

def handler(event, _context) -> Dict:
    """
    Invokes a lambda
    """
    return {
        "statusCode": 200,
        "body": {
            "result": "Hello world",
            "message": "This is sds"
        },
    }
