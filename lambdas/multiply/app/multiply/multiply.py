from typing import Dict

from shared.utils import log_message


def handler(event, _context) -> Dict:
    """Mulitple a by b"""
    param_a = event["a"]
    param_b = event["b"]

    log_message("hello from multiply")

    return {
        "statusCode": 200,
        "body": {
            "result": param_a * param_b,
        },
    }
