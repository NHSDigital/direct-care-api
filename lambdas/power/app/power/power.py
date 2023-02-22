# pylint: disable=R0801
from typing import Dict


def handler(event, _context) -> Dict:
    """Raise a to the power b"""
    param_a = event["a"]
    param_b = event["b"]

    return {
        "statusCode": 200,
        "body": {
            "result": param_a**param_b,
        },
    }
