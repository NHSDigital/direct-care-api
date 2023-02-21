from typing import Dict

from .main.main import handler


def lambda_handler(event, context) -> Dict:
    return handler(event, context)
