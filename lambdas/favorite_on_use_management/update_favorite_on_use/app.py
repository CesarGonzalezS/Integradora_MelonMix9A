import json
import mysql.connector
import os


def lambda_handler(event, context):
    favorite_on_use_id = event['pathParameters']['favorite_on_use_id']
    body = json.loads(event['body'])
    favorite_id = body['favorite_id']
    song_id = body['song_id']
    created_at = body['created_at']

    conn = mysql.connector.connect(
        host=os.environ['RDS_HOST'],
        user=os.environ['RDS_USER'],
        password=os.environ['RDS_PASSWORD'],
        database=os.environ['RDS_DB']
    )

    cursor = conn.cursor()
    query = "UPDATE favorite_on_use SET favorite_id = %s, song_id = %s, created_at = %s WHERE favorite_on_use_id = %s"
    cursor.execute(query, (favorite_id, song_id, created_at, favorite_on_use_id))
    conn.commit()

    return {
        'statusCode': 200,
        'body': json.dumps('Favorite on Use updated successfully!')
    }
