from typing import Dict

from ssp.ssp import handler


def lambda_handler(event, context) -> Dict:
    return handler(event, context)
