import json

from ...app.lib.absolute_file_path import absolute_file_path


def get_mocked_fhir_response(nhs_number):
    mocked_response_file = absolute_file_path(__file__, f"../data/pds_responses/nhs_number_{nhs_number}.json")
    with open(mocked_response_file, "r", encoding="utf-8") as _file:
        return json.loads(_file.read())


class MockGetRequest:

    def __init__(self):
        self.status_code = 200
        self.url = ""
        self.headers = {}

    def json(self):
        response = {f"mocked response not found for url={self.url}"}

        if "personal-demographics" in self.url:
            nhs_number = self.url.split("/")[-1]
            response = get_mocked_fhir_response(nhs_number)

        return response

    def __call__(self, url, headers):
        self.url = url
        self.headers = headers
        return self
