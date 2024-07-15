import json
import logging
from typing import Dict
import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name: str, region_name: str) -> Dict[str, str]:
    """
    Obtiene los secretos almacenados en AWS Secrets Manager.

    Args:
        secret_name (str): El nombre del secreto en AWS Secrets Manager.
        region_name (str): La región de AWS donde se encuentra el secreto.

    Returns:
        dict: Un diccionario con los valores del secreto.
    """
    # Crear un cliente de Secrets Manager
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        logging.error("Error al obtener el secreto: %s", e)
        raise e

    return json.loads(get_secret_value_response['SecretString'])
