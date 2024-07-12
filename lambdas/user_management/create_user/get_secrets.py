# get_secrets.py

import json
import logging
from typing import Dict
import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name: str, region_name: str) -> Dict[str, str]:
    """
    Retrieves the secret value from AWS Secrets Manager.

    Args:
        secret_name (str): The name or ARN of the secret to retrieve.
        region_name (str): The AWS region where the secret is stored.

    Returns:
        dict: The secret value retrieved from AWS Secrets Manager.
    """
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        logging.error("Failed to retrieve secret: %s", e)
        raise e

    return json.loads(get_secret_value_response['SecretString'])
