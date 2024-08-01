import json
import os
from pymysql import Error as MySQLError
from lambdas.user_management.delete_user.get_secrets import get_secret
from lambdas.user_management.delete_user.connection_bd import connect_to_db, execute_query, close_connection

def lambda_handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'OPTIONS, POST, GET, PUT, DELETE',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers
        }

    try:
        body = json.loads(event['body'])
        user_id = body.get('user_id')

        if not user_id:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'message': 'Faltan parámetros obligatorios'})
            }

        try:
            secrets = get_secret(os.getenv('SECRET_NAME'), os.getenv('REGION_NAME'))
            connection = connect_to_db(secrets['host'], secrets['username'], secrets['password'], os.getenv('RDS_DB'))

            query = "DELETE FROM users WHERE user_id = %s"

            if execute_query(connection, query, (user_id,)):
                close_connection(connection)

                if connection.cursor.rowcount > 0:
                    return {
                        'statusCode': 200,
                        'headers': headers,
                        'body': json.dumps({'message': 'Usuario eliminado exitosamente'})
                    }
                else:
                    return {
                        'statusCode': 404,
                        'headers': headers,
                        'body': json.dumps({'message': 'Usuario no encontrado'})
                    }
            else:
                return {
                    'statusCode': 500,
                    'headers': headers,
                    'body': json.dumps({'message': 'Error interno del servidor'})
                }

        except MySQLError as e:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({'message': 'Error de base de datos: ' + str(e)})
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({'message': 'Error interno del servidor: ' + str(e)})
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'message': 'Error interno del servidor: ' + str(e)})
        }
