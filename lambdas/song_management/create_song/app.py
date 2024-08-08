import json
import os
import mysql.connector
from mysql.connector import errorcode

headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST',
    'Access-Control-Allow-Headers': 'Content-Type'
}

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

        data = json.loads(event['body'])
        title = data['title']
        duration = data['duration']
        album_id = data.get('album_id')  # Optional field
        artist_id = data['artist_id']
        genre = data['genre']

        sql = "INSERT INTO songs (title, duration, album_id, artist_id, genre) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (title, duration, album_id, artist_id, genre))
        connection.commit()

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps('Song created successfully')
        }
    except KeyError as e:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps(f'Bad request. Missing required parameters: {str(e)}')
        }
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps('Something is wrong with your user name or password')
            }
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps('Database does not exist')
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps(f'Database error: {str(err)}')
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()
