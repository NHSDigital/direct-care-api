import requests

REQUEST_TIMEOUT = 2


def make_get_request(url, headers):
    """Extracted function to make mocking requests easier"""
    return requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)


def make_post_request(url, data, headers):
    """Extracted function to make mocking requests easier"""
    return requests.post(url, data=data, headers=headers, timeout=REQUEST_TIMEOUT)
