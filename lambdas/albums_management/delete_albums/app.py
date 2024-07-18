import json
import os
from pymysql import Error as MySQLError
from get_secrets import get_secret
from connection_bd import connect_to_db, execute_query, close_connection

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        album_id = body.get('album_id')

        if not album_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Faltan parámetros obligatorios'})
            }

        try:
            secrets = get_secret(os.getenv('SECRET_NAME'), os.getenv('REGION_NAME'))
            connection = connect_to_db(secrets['host'], secrets['username'], secrets['password'], os.getenv('RDS_DB'))

            query = "DELETE FROM albums WHERE album_id = %s"

            if execute_query(connection, query, (album_id,)):
                if connection.cursor().rowcount > 0:
                    close_connection(connection)
                    return {
                        'statusCode': 200,
                        'body': json.dumps({'message': 'Álbum eliminado exitosamente'})
                    }
                else:
                    close_connection(connection)
                    return {
                        'statusCode': 404,
                        'body': json.dumps({'message': 'Álbum no encontrado'})
                    }
            else:
                close_connection(connection)
                return {
                    'statusCode': 500,
                    'body': json.dumps({'message': 'Error interno del servidor'})
                }

        except MySQLError as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'Error de base de datos: ' + str(e)})
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'Error interno del servidor: ' + str(e)})
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error interno del servidor: ' + str(e)})
        }