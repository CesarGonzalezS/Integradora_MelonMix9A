import json
import boto3
import pymysql
from botocore.exceptions import ClientError
from lambdas.user_management.read_user.connection_bd import connect_to_db, execute_query
from lambdas.user_management.read_user.get_secrets import get_secret

def read_users(username=None):
    try:
        # Obtener secretos de AWS Secrets Manager
        secrets = get_secret()

        # Conectarse a la base de datos
        connection = connect_to_db(secrets)

        # Construir la consulta
        if username:
            query = "SELECT * FROM users WHERE username = %s"
            params = (username,)
        else:
            query = "SELECT * FROM users"
            params = None

        # Ejecutar la consulta
        users = execute_query(connection, query, params)

        # Cerrar la conexión
        connection.close()

        return users
    except ClientError as e:
        print(f"Error obtaining secret: {e}")
        raise e
    except pymysql.MySQLError as e:
        print(f"Error connecting to MySQL: {e}")
        raise e

def lambda_handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'OPTIONS, POST, GET, PUT, DELETE',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers
        }

    try:
        # Obtener el parámetro `username` del evento
        username = event.get('username')

        # Leer usuarios
        users = read_users(username)

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(users)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }
