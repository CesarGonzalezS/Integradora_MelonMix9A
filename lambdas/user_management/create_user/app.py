import json
import os
import datetime
from lambdas.user_management.create_user.get_secrets import get_secret
from lambdas.user_management.create_user.connection_bd import connect_to_db, execute_query, close_connection

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])

        username = body.get('username')
        email = body.get('email')
        password = body.get('password')
        date_joined = body.get('date_joined')

        if not username or not email or not password or not date_joined:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Faltan parámetros obligatorios'})
            }

        if '@' not in email:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Correo electrónico no válido'})
            }

        try:
            date_joined = datetime.datetime.strptime(date_joined, '%Y-%m-%d')
        except ValueError:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Fecha de unión no válida'})
            }

        try:
            secrets = get_secret(os.getenv('SECRET_NAME'), os.getenv('REGION_NAME'))
            connection = connect_to_db(secrets['host'], secrets['username'], secrets['password'], os.getenv('RDS_DB'))

            query = f"INSERT INTO users (username, email, password, date_joined) VALUES ('{username}', '{email}', '{password}', '{date_joined}')"
            execute_query(connection, query)

            close_connection(connection)

            return {
                'statusCode': 201,
                'body': json.dumps({'message': 'Usuario creado exitosamente'})
            }
        except Exception as e:
            # Log the exception for debugging purposes
            print(f"Unexpected error: {str(e)}")

            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'Error interno del servidor'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error interno del servidor'})
        }
