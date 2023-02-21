from typing import Dict

from shared.logger.lambda_context_logging_filter import LambdaContextLoggingFilter
from shared.logger import log_action, app_logger

context_logger = LambdaContextLoggingFilter()
app_logger.setup("multiply_lambda")
app_logger.logger().addFilter(context_logger)


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
