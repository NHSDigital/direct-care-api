import logging
import os
import secrets
import sys
from logging import DEBUG, INFO

if not os.getenv("BASE_URL"):
    BASE_URL = "cookieclickertechtest.airelogic.com"
else:
    BASE_URL = os.getenv("BASE_URL")


def before_all(context):
    if is_debug(context):
        setup_logging(level=DEBUG)
    else:
        setup_logging(level=INFO)
    context.base_url = generate_url()


def after_all(context):
    pass


def setup_logging(level: int = logging.INFO):
    handlers = [logging.StreamHandler(sys.stdout)]
    logging.basicConfig(
        format="[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
        level=level,
        handlers=handlers,
    )


def is_debug(context):
    try:
        debug = context.config.userdata["debug"]
    except KeyError:
        print("Running in Normal mode")
        return False
    if str(debug) == "True":
        print("Running in DEBUG mode")
        return True
    else:
        print("Running in Normal mode")
        return False


def generate_url():
    project_name = os.path.basename(os.getcwd())
    url = f"https://{project_name}-{secrets.token_urlsafe(30*3//4)}.{BASE_URL}"
    return url
