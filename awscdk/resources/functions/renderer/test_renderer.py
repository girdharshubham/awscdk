import os, boto3, pytest
from moto import mock_aws
from awscdk.resources.functions.renderer.renderer import handler


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture
def ssm(aws_credentials):
    with mock_aws():
        yield boto3.client("ssm")


def test_renderer(ssm):
    values = [
        {"name": "/platform/account/env", "value": "development", "result": 1},
        {"name": "/platform/account/env", "value": "staging", "result": 2},
        {"name": "/platform/account/env", "value": "production", "result": 2},
    ]

    for value in values:
        ssm.put_parameter(Name=value["name"], Value=value["value"], Type="String")
        result = handler({"parameter_name": "/platform/account/env"}, None)

        assert result["Data"]["values"]["controller"]["replicaCount"] == value["result"]

        ssm.delete_parameter(Name="/platform/account/env")
