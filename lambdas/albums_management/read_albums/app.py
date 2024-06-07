import json
import os
import mysql.connector

def lambda_handler(event, context):
    try:

        db_host = os.environ['RDS_HOST']
        db_user = os.environ['RDS_USER']
        db_password = os.environ['RDS_PASSWORD']
        db_name = os.environ['RDS_DB']


        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )

        cursor = connection.cursor()

        album_id = event['pathParameters']['album_id']

        # Consulta SQL para obtener la información del álbum
        sql = "SELECT * FROM albums WHERE album_id = %s"
        cursor.execute(sql, (album_id,))
        album = cursor.fetchone()

        if album:

            album_dict = {
                'album_id': album[0],
                'title': album[1],
                'release_date': album[2].strftime('%Y-%m-%d'),
                'artist_id': album[3]
            }
            return {
                'statusCode': 200,
                'body': json.dumps(album_dict)
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('Album not found')
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }
    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()