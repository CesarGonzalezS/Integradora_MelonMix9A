import json
import mysql.connector
import os


def lambda_handler(event, context):
    favorite_on_use_id = event['pathParameters']['favorite_on_use_id']

    conn = mysql.connector.connect(
        host=os.environ['RDS_HOST'],
        user=os.environ['RDS_USER'],
        password=os.environ['RDS_PASSWORD'],
        database=os.environ['RDS_DB']
    )

    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM favorite_on_use WHERE favorite_on_use_id = %s"
    cursor.execute(query, (favorite_on_use_id,))
    result = cursor.fetchone()

    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
