import requests


def make_get_request(url, headers):
    """Extracted function to make mocking requests easier"""
    return requests.get(url, headers=headers, timeout=600)
