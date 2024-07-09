import json
import os
import base64
from pymysql import connect, Error as MySQLError
from datetime import datetime

def get_connection():
    return connect(
        host=os.environ['RDS_HOST'],
        user=os.environ['RDS_USER'],
        password=os.environ['RDS_PASSWORD'],
        database=os.environ['RDS_DB']
    )

def lambda_handler(event, context):
    connection = None
    try:
        body = json.loads(event['body'])
        username = body.get('username')
        email = body.get('email')
        password = body.get('password')
        date_joined = body.get('date_joined')
        profile_image_binary = body.get('profile_image_binary')

        # Validaciones de parámetros obligatorios
        if not all([username, email, password, date_joined, profile_image_binary]):
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Faltan parámetros obligatorios'})
            }

        # Validación de correo electrónico
        if '@' not in email:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Correo electrónico no válido'})
            }

        # Validación de fecha
        try:
            datetime.strptime(date_joined, '%Y-%m-%d')
        except ValueError:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Fecha de unión no válida'})
            }

        # Convertir la imagen binaria a base64
        try:
            profile_image_base64 = base64.b64encode(profile_image_binary.encode('utf-8')).decode('utf-8')
        except Exception as e:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Error al codificar la imagen a base64: ' + str(e)})
            }

        # Creación de usuario en la base de datos
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO users (username, email, password, date_joined, profile_image_base64) 
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (username, email, password, date_joined, profile_image_base64))
            connection.commit()
            return {
                'statusCode': 201,
                'body': json.dumps({'message': 'Usuario creado exitosamente'})
            }
        except MySQLError as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'Error de base de datos: ' + str(e)})
            }
        finally:
            if connection:
                connection.close()

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error interno del servidor: ' + str(e)})
        }
