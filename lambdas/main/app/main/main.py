import asyncio
import json
import os
from typing import Dict, Tuple

import boto3
from shared.logger import app_logger, log_action
from shared.logger.lambda_context_logging_filter import LambdaContextLoggingFilter

context_logger = LambdaContextLoggingFilter()
app_logger.setup("main_lambda")
app_logger.logger().addFilter(context_logger)


@log_action()
async def add(lambda_client, param_a: int, param_b: int) -> Tuple[str, int]:
    """Async function to invoke the Add lambda"""
    lambda_payload = {"a": param_a, "b": param_b}
    response = lambda_client.invoke(
        FunctionName="AddFunction",
        InvocationType="RequestResponse",
        Payload=json.dumps(lambda_payload).encode("utf-8"),
    )
    response_payload = json.loads(response["Payload"].read().decode("utf-8"))
    return "add", response_payload["body"]["result"]


@log_action()
async def multiply(lambda_client, param_a: int, param_b: int) -> Tuple[str, int]:
    """Async function to invoke the Multiply lambda"""
    lambda_payload = {"a": param_a, "b": param_b}
    response = lambda_client.invoke(
        FunctionName="MultiplyFunction",
        InvocationType="RequestResponse",
        Payload=json.dumps(lambda_payload).encode("utf-8"),
    )
    response_payload = json.loads(response["Payload"].read().decode("utf-8"))
    return "multiply", response_payload["body"]["result"]


@log_action()
async def power(lambda_client, param_a: int, param_b: int) -> Tuple[str, int]:
    """Async function to invoke the Power lambda"""
    lambda_payload = {"a": param_a, "b": param_b}
    response = lambda_client.invoke(
        FunctionName="PowerFunction",
        InvocationType="RequestResponse",
        Payload=json.dumps(lambda_payload).encode("utf-8"),
    )
    response_payload = json.loads(response["Payload"].read().decode("utf-8"))
    return "power", response_payload["body"]["result"]


@log_action()
async def pds(lambda_client, nhs_number: int) -> Tuple[str, int]:
    """Async function to invoke the Personal Demogrpahic Service lambda"""
    lambda_payload = {"nhs_number": nhs_number}
    response = lambda_client.invoke(
        FunctionName="PdsFunction",
        InvocationType="RequestResponse",
        Payload=json.dumps(lambda_payload).encode("utf-8"),
    )
    response_payload = json.loads(response["Payload"].read().decode("utf-8"))
    return "pds", response_payload["body"]["result"]


@log_action()
async def process(event: Dict) -> Dict:
    """Orchestration function"""

    is_sam_local = os.getenv("AWS_SAM_LOCAL") == "true"
    lambda_client = (
        boto3.client("lambda", endpoint_url=os.getenv("EndpointUrl"))
        if is_sam_local
        else boto3.client("lambda")
    )

    param_a = int(event["queryStringParameters"]["a"])
    param_b = int(event["queryStringParameters"]["b"])
    nhs_number = int(event["queryStringParameters"]["nhs_number"])

    results = await asyncio.gather(
        add(lambda_client, param_a, param_b),
        multiply(lambda_client, param_a, param_b),
        power(lambda_client, param_a, param_b),
        pds(lambda_client, nhs_number),
    )
    print({result[0]: result[1] for result in results})
    return {result[0]: result[1] for result in results}


@log_action()
def handler(event, _context) -> Dict:
    """Lambda entry point"""
    return {
        "statusCode": 200,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(asyncio.run(process(event))),
    }
