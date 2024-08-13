import json
import os
import mysql.connector

headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type'
}

def lambda_handler(event, context):
    try:
        db_user = os.environ['RDS_USER']
        db_host = os.environ['RDS_HOST']
        db_password = os.environ['RDS_PASSWORD']
        db_name = os.environ['RDS_DB']

        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )

        cursor = connection.cursor()


        sql = "SELECT * FROM songs"
        cursor.execute(sql)

        songs = cursor.fetchall()

        songs_list = []

        for song in songs:
            song_dict = {
                'song_id': song[0],
                'title': song[1],
                'duration': song[2],
                'album_id': song[3],
                'artist_id': song[4],
                'genre': song[5]
            }
            songs_list.append(song_dict)

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(songs_list)
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
