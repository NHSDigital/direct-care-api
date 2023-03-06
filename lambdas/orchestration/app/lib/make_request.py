import requests


def make_get_request(url, headers, params=None):
    """Extracted function to make mocking requests easier"""
    return requests.get(url, headers=headers, params=params, timeout=600)


def make_post_request(url, data, headers):
    """Extracted function to make mocking requests easier"""
    return requests.post(url, data=data, headers=headers, timeout=600)
