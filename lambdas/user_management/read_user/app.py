import json
import boto3
import pymysql
from botocore.exceptions import ClientError
from lambdas.user_management.read_user.connection_bd import connect_to_db, execute_query

headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type'
}

def read_users(username=None):
    try:

        # Conectarse a la base de datos
        connection = connect_to_db()

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
    except Exception as e:
        raise e


def lambda_handler(event, context):
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