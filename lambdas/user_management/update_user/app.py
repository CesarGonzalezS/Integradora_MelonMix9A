import json
import boto3
import pymysql
from botocore.exceptions import ClientError
from lambdas.user_management.update_user.connection_bd import connect_to_db, execute_query
from lambdas.user_management.update_user.get_secrets import get_secret


def lambda_handler(event, context):
    try:
        # Extraer parámetros del evento
        user_id = event.get('user_id')
        username = event.get('username')
        email = event.get('email')
        password = event.get('password')

        # Validar los parámetros necesarios
        if not user_id or not username or not email or not password:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Faltan parámetros requeridos'})
            }

        # Obtener credenciales de la base de datos
        secret_name = "db_credentials"  # Nombre del secreto en AWS Secrets Manager
        secrets = get_secret(secret_name)
        db_host = secrets['host']
        db_user = secrets['username']
        db_password = secrets['password']
        db_name = secrets['dbname']

        # Conectar a la base de datos
        connection = connect_to_db(db_host, db_user, db_password, db_name)

        # Consulta SQL para actualizar el usuario
        update_query = """
        UPDATE users
        SET username = %s, email = %s, password = %s
        WHERE user_id = %s
        """
        execute_query(connection, update_query, (username, email, password, user_id))

        # Cerrar la conexión a la base de datos
        connection.close()

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Usuario actualizado exitosamente'})
        }

    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error al acceder a Secrets Manager: {str(e)}'})
        }
    except pymysql.MySQLError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error en la base de datos: {str(e)}'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error inesperado: {str(e)}'})
        }
