import os

# Set required env vars before anything imports the app
os.environ["FROM_EMAIL"] = "test-from@example.com"
os.environ["DESTINATION_EMAIL"] = "test-dest@example.com"
os.environ["FORM_SHARED_SECRET"] = "test-secret"
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

import pytest  # noqa: E402


@pytest.fixture
def aws_credentials():
    """Env vars are already set at module level for moto."""
