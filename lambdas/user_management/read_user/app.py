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

        # Consulta para obtener todos los usuarios
        sql = "SELECT user_id, username, email, password, date_joined, profile_image_base64 FROM users"
        cursor.execute(sql)
        users = cursor.fetchall()

        if users:
            users_list = []
            for user in users:
                # Convertir la fecha a cadena de texto antes de serializar a JSON
                user_date_joined_str = user[4].strftime('%Y-%m-%d')
                user_dict = {
                    'user_id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'password': user[3],
                    'date_joined': user_date_joined_str,
                    'profile_image_base64': user[5]  # Añadir la imagen en base64
                }
                users_list.append(user_dict)

            return {
                'statusCode': 200,
                'body': json.dumps(users_list)
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('No users found')
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
