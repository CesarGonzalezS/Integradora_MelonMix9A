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

        song_id = event['pathParameters']['song_id']

        sql = "SELECT * FROM songs WHERE song_id = %s"
        cursor.execute(sql, (song_id,))
        song = cursor.fetchone()

        if song:
            song_dict = {
                'song_id': song[0],
                'title': song[1],
                'duration': song[2],
                'album_id': song[3],
                'artist_id': song[4],
                'genre': song[5]
            }
            return {
                'statusCode': 200,
                'body': json.dumps(song_dict)
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('Song not found')
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
