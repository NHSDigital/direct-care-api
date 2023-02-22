from typing import Dict

from shared.logger import app_logger, log_action
from shared.logger.lambda_context_logging_filter import LambdaContextLoggingFilter

from .main.main import handler

context_logger = LambdaContextLoggingFilter()
app_logger.setup("main_lambda")
app_logger.logger().addFilter(context_logger)


@log_action(log_args=["event", "context"])
def lambda_handler(event, context) -> Dict:
    return handler(event, context)
