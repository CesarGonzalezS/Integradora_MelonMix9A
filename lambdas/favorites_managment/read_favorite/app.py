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

        favorite_id = event['pathParameters']['favorite_id']

        sql = "SELECT * FROM favorites WHERE favorite_id  = %s"
        cursor.execute(sql, (favorite_id,))
        favorite = cursor.fetchone()

        if favorite:
            # Convertir la fecha a cadena de texto antes de serializar a JSON
            favorite_date_joined_str = favorite[3].strftime('%Y-%m-%d')
            favorite_dict = {
                'favorite_id': favorite[0],
                'description': favorite[1],
                'user_id': favorite[2],
                'created_at': favorite_date_joined_str
            }
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(favorite_dict)
            }
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps('favorite not found')
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
