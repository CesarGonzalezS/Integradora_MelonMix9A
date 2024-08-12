import json
import os
import mysql.connector
from datetime import date

headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type'
}

def lambda_handler(event, context):
    # Obtener variables de entorno
    db_host = os.environ['RDS_HOST']
    db_user = os.environ['RDS_USER']
    db_password = os.environ['RDS_PASSWORD']
    db_name = os.environ['RDS_DB']

    # Conexión a la base de datos
    try:
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )

        cursor = connection.cursor()

        user_id = event['pathParameters']['user_id']

        sql = """
        SELECT f.favorite_id, f.description, f.user_id, f.created_at, 
               s.song_id, s.title, s.duration, s.album_id, s.artist_id, s.genre
        FROM favorites f
        JOIN songs s ON f.favorite_id = s.song_id
        WHERE f.user_id = %s
        """
        cursor.execute(sql, (user_id,))
        favorites = cursor.fetchall()

        if favorites:
            favorites_list = []
            for favorite in favorites:
                favorite_dict = {
                    'favorite_id': favorite[0],
                    'description': favorite[1],
                    'user_id': favorite[2],
                    'created_at': favorite[3].strftime('%Y-%m-%d'),
                    'song': {
                        'song_id': favorite[4],
                        'title': favorite[5],
                        'duration': favorite[6],
                        'album_id': favorite[7],
                        'artist_id': favorite[8],
                        'genre': favorite[9]
                    }
                }
                favorites_list.append(favorite_dict)

            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(favorites_list)
            }
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps('No favorites found for this user')
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps(f"Error: {str(e)}")
        }
    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()