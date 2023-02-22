from typing import Dict
from pds.pds import handler


def lambda_handler(event, context) -> Dict:
    return handler(event, context)
