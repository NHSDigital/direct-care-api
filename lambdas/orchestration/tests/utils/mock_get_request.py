import json
import pathlib
from http import HTTPStatus

from ...app.lib.absolute_file_path import absolute_file_path


def get_mocked_fhir_response(nhs_number):

    status_code = HTTPStatus.OK
    content = {}

    data_dir = absolute_file_path(__file__, "../data/pds_responses/")
    mocked_response_file = pathlib.Path(data_dir) / f"nhs_number_{nhs_number}.json"

    if nhs_number == "0000000000":
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        # Not sure exactly what the body of a PDS error looks like so leave blank for now
        content = {}

    elif not pathlib.Path.exists(mocked_response_file):
        status_code = HTTPStatus.BAD_REQUEST
        error_file = pathlib.Path(data_dir) / "not_found_response.json"
        with open(error_file, "r", encoding="utf-8") as _file:
            content = _file.read()

    else:
        with open(mocked_response_file, "r", encoding="utf-8") as _file:
            status_code = HTTPStatus.OK
            content = json.loads(_file.read())

    return status_code, content


class MockGetRequest:

    def __init__(self):
        self.url = ""
        self.headers = {}

    def json(self):
        return self.response

    def __call__(self, url, headers, *args, **kwargs):
        self.url = url
        self.headers = headers

        self.status_code = 200
        self.response = {f"mocked response not found for url={self.url}"}

        if "personal-demographics" in self.url:
            nhs_number = self.url.split("/")[-1]
            self.status_code, self.response = get_mocked_fhir_response(nhs_number)

        return self
