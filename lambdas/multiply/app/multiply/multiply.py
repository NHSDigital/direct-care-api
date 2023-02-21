from typing import Dict

from shared.logger import log_action


@log_action()
def handler(event, _context) -> Dict:
    """Mulitple a by b"""
    param_a = event["a"]
    param_b = event["b"]

    return {
        "statusCode": 200,
        "body": {
            "result": param_a * param_b,
        },
    }
