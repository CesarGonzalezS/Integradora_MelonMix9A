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

        sql = "SELECT * FROM artists"
        cursor.execute(sql)
        results = cursor.fetchall()

        artists = []
        for artist in results:
            artist_dict = {
                'artist_id': artist[0],
                'name': artist[1],
                'genre': artist[2],
                'bio': artist[3]
            }
            artists.append(artist_dict)

        return {
            'statusCode': 200,
            'body': json.dumps(artists)
        }
    except mysql.connector.Error as err:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Database error: {str(err)}")
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
