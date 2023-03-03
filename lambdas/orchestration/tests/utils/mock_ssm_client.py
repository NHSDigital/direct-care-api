from botocore.exceptions import ClientError

from .mock_private_key import MOCK_RSA_KEY


class MockSSMClient:
    """Mocking SSM Client"""

    def __init__(self) -> None:
        self.params = {"apim_api_key": "12345", "apim_private_key": MOCK_RSA_KEY}

    def get_parameter(self, Name, **kwargs):
        """Mocking the get_parameter function"""
        if Name not in self.params:
            raise ClientError({"Error": {"Message": f"Parameter {Name} not found."}}, "testing")
        return {"Parameter": {"Value": self.params[Name]}}

    def __call__(self, *args):
        return self
