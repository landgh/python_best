'''
ledin@land-gram MINGW64 /d/mypython/python_best (main)
pytest --log-cli-level=INFO tests/test_my_lambda_pytest.py
'''
import logging
import os
import boto3
import pytest
from moto import mock_s3 # pip install "moto<5"

from src.my_lambda import lambda_handler

logging.basicConfig(level=logging.INFO)
# logging.getLogger().setLevel(logging.DEBUG)
# logging.getLogger("botocore").setLevel(logging.DEBUG)

@pytest.fixture(autouse=True)
def mock_aws_env_vars(monkeypatch):
    # Set up dummy AWS credentials
    for var in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN", "AWS_DEFAULT_REGION"]:
        logging.info(f"Deleting {os.getenv(var)} from environment variables")
        monkeypatch.delenv(var, raising=False)

    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "fake-access-key-id")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "fake-secret-access-key")
    # monkeypatch.setenv("AWS_SESSION_TOKEN", "fake-session-token")  # Optional
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    logging.info(f"AWS_SECRTE_ACCESS_KEY is set up by monkeypatch: {os.getenv('AWS_SECRET_ACCESS_KEY')}")

    yield

    logging.info(f"AWS_SECRTE_ACCESS_KEY during teardown set up by monkeypatch: {os.getenv('AWS_SECRET_ACCESS_KEY')}")

@pytest.fixture
# since we used @pytest.fixture(autouse=True) in mock_aws_env_vars, we don't need to inject it in the test function.
# Otherwise, we need to use s3_setup(mock_aws_env_vars)
def s3_setup():
    with mock_s3():
        for var in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN", "AWS_DEFAULT_REGION"]:
            logging.info(f"getting {os.getenv(var)} from environment variables")

        # Create mock S3 client
        s3 = boto3.client('s3', 
            region_name="us-east-1",
            aws_access_key_id="fake-access-key-id",
            aws_secret_access_key="fake-secret-key");
        
        # Create source and target buckets
        source_bucket = "source-bucket"
        target_bucket = "source-bucket"  # Using the same bucket by default
        s3.create_bucket(Bucket=source_bucket)
        
        # Upload a file to the source bucket
        source_key = "input.txt"
        s3.put_object(Bucket=source_bucket, Key=source_key, Body="Hello World!")
        
        yield s3, source_bucket, target_bucket, source_key


def test_my_lambda_pytest(s3_setup):
    logging.info(f"test_my_lambda_pytest is called...........................................")
    """Test the Lambda function."""
    s3, source_bucket, target_bucket, source_key = s3_setup

    # Mock event
    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {
                        "name": source_bucket
                    },
                    "object": {
                        "key": source_key
                    }
                }
            }
        ]
    }

    # Run the Lambda function
    response = lambda_handler(event, None)
    logging.info(f"response is {response}")

    # Assert the response is successful
    assert response['statusCode'] == 200

    # Verify the processed file is saved to S3
    processed_key = f"processed/{source_key}"
    obj = s3.get_object(Bucket=target_bucket, Key=processed_key)
    processed_content = obj['Body'].read().decode('utf-8')

    # Assert the processed content is correct
    assert processed_content == "HELLO WORLD!"