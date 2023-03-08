# pylint: disable=duplicate-code

import json
import pathlib
from http import HTTPStatus

from ...app.lib.absolute_file_path import absolute_file_path
from ...app.lib.get_dict_value import get_dict_value


def get_mocked_ssp_response(nhs_number):
    status_code = HTTPStatus.OK
    content = {}

    data_dir = absolute_file_path(__file__, "../data/ssp_responses/")
    mocked_response_file = pathlib.Path(data_dir) / f"ssp_response_{nhs_number}.json"

    if nhs_number == "1111111111":
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        # Not sure exactly what the body of a SSP error looks like so leave blank for now
        content = {}

    elif not pathlib.Path.exists(mocked_response_file):
        status_code = HTTPStatus.NOT_FOUND
        error_file = pathlib.Path(data_dir) / "ssp_not_found_response.json"
        with open(error_file, "r", encoding="utf-8") as _file:
            content = _file.read()

    else:
        with open(mocked_response_file, "r", encoding="utf-8") as _file:
            status_code = HTTPStatus.OK
            content = json.loads(_file.read())

    return status_code, content


class MockPostRequest:
    """Process incoming post requests and send back the correct mocked response"""

    def __init__(self):
        self.url = ""
        self.headers = {}
        self.status_code = None
        self.response = {}
        self.body = json.dumps({})

    def json(self):
        return self.response

    def __call__(self, url, headers, *args, **kwargs):
        self.url = url
        self.headers = headers
        self.body = kwargs.get("data") or self.body
        self.status_code = 200
        self.response = {"error": f"mocked response not found for url={self.url}"}

        if "gpconnect/structured" in self.url:
            nhs_number = get_dict_value(json.loads(self.body), "/parameter/0/valueIdentifier/value")
            self.status_code, self.response = get_mocked_ssp_response(nhs_number)

        return self
