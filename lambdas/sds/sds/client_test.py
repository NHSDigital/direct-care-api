from unittest import mock
from .sds import DEVICE_URL, get_sds_device_data

def mocked_requests_get(url):
    class MockResponse: # pylint: disable=too-few-public-methods
        """This"""
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if url == f"{DEVICE_URL}/1234":
        return MockResponse({"key1": "value1"}, 200)
    if url == f"{DEVICE_URL}/1235":
        return MockResponse({"key2": "value2"}, 400)

    return MockResponse(None, 404)


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_200():
    response = get_sds_device_data(1234)
    assert response.status_code == 200


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_400():
    response = get_sds_device_data(1235)
    assert response.status_code == 400
