from typing import Dict

from multiply.multiply import handler


def lambda_handler(event, context) -> Dict:
    return handler(event, context)
