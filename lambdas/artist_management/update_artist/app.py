import json
import os
import mysql.connector

headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'PUT',
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
        artist_id = data['artist_id']
        name = data.get('name')
        genre = data.get('genre')
        bio = data.get('bio')

        sql = f"UPDATE artists SET name = %s, genre = %s, bio = %s WHERE artist_id = %s"
        cursor.execute(sql, (name, genre, bio, artist_id))
        connection.commit()

        return {
            'statusCode': 200,
            'Headers': headers,
            'body': json.dumps('Artist updated successfully')
        }
    except KeyError:
        return {
            'statusCode': 400,
            'Headers': headers,
            'body': json.dumps('Bad request. Missing required parameters.')
        }
    except mysql.connector.Error as err:
        return {
            'statusCode': 500,
            'Headers': headers,
            'body': json.dumps(f"Database error: {str(err)}")
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'Headers': headers,
            'body': json.dumps(f"Error: {str(e)}")
        }
    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()
