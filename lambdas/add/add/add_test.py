from .add import handler


def test_lambda_handler():
    ret = handler({"a": 4, "b": 5}, {})
    body = ret["body"]

    assert ret["statusCode"] == 200
    assert "result" in body
    assert body["result"] == 9
