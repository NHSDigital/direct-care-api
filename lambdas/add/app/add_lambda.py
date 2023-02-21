from typing import Dict
from .add.add import handler


def lambda_handler(event, context) -> Dict:
    return handler(event, context)
