import requests


def test_lambda_handler():
    # Requests `make start-api` and 'make start-lambda' to be running
    response = requests.get("http://localhost:3000/calculate?a=3&b=5", timeout=30)
    assert response.status_code == 200
    assert response.json() == {"add": 8, "multiply": 15, "power": 243}
