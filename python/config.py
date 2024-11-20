import logging
import os
import boto3
from botocore.exceptions import ClientError
import base64
import json

logger = logging.getLogger()

ENVIRONMENT = os.environ["Environment"]
PROJECT = os.environ["Project"]
ACCESS_TOKEN = f"{PROJECT}-secrets-{ENVIRONMENT}"


def get_secret():
    session = boto3.session.Session()
    sm = session.client(service_name="secretsmanager", region_name="eu-west-1")

    try:
        response = sm.get_secret_value(SecretId=ACCESS_TOKEN)
        secret_value = response.get("SecretString") or base64.b64decode(
            response["SecretBinary"]
        )
        return json.loads(secret_value)
    except ClientError as e:
        logger.error(f"Failed to retrieve secret: {e.response['Error']['Code']}")
        raise
