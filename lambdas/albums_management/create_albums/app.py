import json
import os
import mysql.connector
from lambdas.album_management.create_album.get_secrets import get_secret
from lambdas.album_management.create_album.connection_bd import connect_to_db, execute_query, close_connection

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])

        title = body.get('title')
        release_date = body.get('release_date')
        artist_id = body.get('artist_id')

        if not title or not release_date or not artist_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Faltan parámetros obligatorios'})
            }

        try:
            release_date = datetime.datetime.strptime(release_date, '%Y-%m-%d')
        except ValueError:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Fecha de lanzamiento no válida'})
            }

        try:
            secrets = get_secret(os.getenv('SECRET_NAME'), os.getenv('REGION_NAME'))
            connection = connect_to_db(secrets['host'], secrets['username'], secrets['password'], os.getenv('RDS_DB'))

            query = "INSERT INTO albums (title, release_date, artist_id) VALUES (%s, %s, %s)"
            execute_query(connection, query, (title, release_date, artist_id))

            close_connection(connection)

            return {
                'statusCode': 201,
                'body': json.dumps({'message': 'Álbum creado exitosamente'})
            }
        except mysql.connector.Error as err:
            return {
                'statusCode': 500,
                'body': json.dumps({'message': f'Error en la base de datos: {str(err)}'})
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
