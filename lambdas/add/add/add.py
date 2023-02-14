from typing import Dict


def handler(event, _context) -> Dict:
    """Add a to b"""
    param_a = event["a"]
    param_b = event["b"]

    return {
        "statusCode": 200,
        "body": {
            "result": param_a + param_b,
        },
    }
