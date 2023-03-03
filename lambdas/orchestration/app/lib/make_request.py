import requests


def make_get_request(url, headers):
    """Extracted function to make mocking requests easier"""
    return requests.get(url, headers=headers, timeout=600)


def make_post_request(url, data, headers):
    """Extracted function to make mocking requests easier"""
    return requests.get(url, data=data, headers=headers, timeout=600)
