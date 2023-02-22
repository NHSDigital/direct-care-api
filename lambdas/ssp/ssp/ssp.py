from typing import Dict
import requests


SANDBOX_URL = ""


def handler(event, _context) -> Dict:
    """Invoke ssp Lambda"""
    ssp_input = event["ssp_input"]

    return {
        "statusCode": 200,
        "body": {
            "result": ssp_input,
        },
    }
