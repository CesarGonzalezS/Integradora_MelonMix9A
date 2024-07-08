import json
import os
import mysql.connector
from datetime import date

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

        if 'pathParameters' in event and 'user_id' in event['pathParameters']:
            user_id = event['pathParameters']['user_id']
        elif 'user_id' in event:
            user_id = event['user_id']
        else:
            return {
                'statusCode': 400,
                'body': json.dumps('Missing user_id parameter')
            }

        sql = "SELECT * FROM users WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        user = cursor.fetchone()

        if user:
            # Convertir la fecha a cadena de texto antes de serializar a JSON
            user_date_joined_str = user[4].strftime('%Y-%m-%d')
            user_dict = {
                'user_id': user[0],
                'username': user[1],
                'email': user[2],
                'password': user[3],
                'date_joined': user_date_joined_str
            }
            return {
                'statusCode': 200,
                'body': json.dumps(user_dict)
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('User not found')
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
