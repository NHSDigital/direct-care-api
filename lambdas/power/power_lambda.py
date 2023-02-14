from typing import Dict

from power.power import handler


def lambda_handler(event, context) -> Dict:
    return handler(event, context)
