from typing import Dict
from shared.logger.lambda_context_logging_filter import LambdaContextLoggingFilter
from shared.logger import log_action, app_logger

from .multiply.multiply import handler

context_logger = LambdaContextLoggingFilter()

app_logger.setup("multiply_lambda")
app_logger.logger().addFilter(context_logger)


@log_action(log_args=["event", "context"])
def lambda_handler(event, context) -> Dict:
    context_logger.context = context
    return handler(event, context)
