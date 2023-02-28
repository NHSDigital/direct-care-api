from typing import Dict

from sds.sds import handler


def lambda_handler(event, context) -> Dict:
    return handler(event, context)
