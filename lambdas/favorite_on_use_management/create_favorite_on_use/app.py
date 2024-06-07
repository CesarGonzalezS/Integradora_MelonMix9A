import json
import mysql.connector
import os


def lambda_handler(event, context):
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
    query = "INSERT INTO favorite_on_use (favorite_id, song_id, created_at) VALUES (%s, %s, %s)"
    cursor.execute(query, (favorite_id, song_id, created_at))
    conn.commit()

    return {
        'statusCode': 200,
        'body': json.dumps('Favorite on Use created successfully!')
    }
