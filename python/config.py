import logging
import os
import boto3
from botocore.exceptions import ClientError
import base64

logger = logging.getLogger()

ENVIRONMENT = os.environ["Environment"]
PROJECT = os.environ["Project"]
ACCESS_TOKEN = f"ACCESS_TOKEN-{PROJECT}-{ENVIRONMENT}"

def get_secret():
    session = boto3.session.Session()
    sm = session.client(service_name="secretsmanager", region_name="eu-west-1")
    
    try:
        response = sm.get_secret_value(SecretId=ACCESS_TOKEN)
        return response.get("SecretString") or base64.b64decode(response["SecretBinary"])
    except ClientError as e:
        logger.error(f"Failed to retrieve secret: {e.response['Error']['Code']}")
        raise
