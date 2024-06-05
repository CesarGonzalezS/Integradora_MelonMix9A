import json
import mysql.connector
import os
from datetime import datetime

def lambda_handler(event, context):
    # Obtener variables de entorno
    db_host = os.environ['RDS_HOST']
    db_user = os.environ['RDS_USER']
    db_password = os.environ['RDS_PASSWORD']
    db_name = os.environ['RDS_DB']

    # Obtener datos del usuario del evento
    try:
        body = json.loads(event['body'])
        username = body['username']
        email = body['email']
        password = body['password']
    except (KeyError, json.JSONDecodeError) as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Invalid input",
                "error": str(e)
            })
        }

    # Conectar a la base de datos RDS
    try:
        conn = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        cursor = conn.cursor()

        # Insertar un nuevo usuario
        date_joined = datetime.now().strftime('%Y-%m-%d')
        insert_query = """
            INSERT INTO users (username, email, password, date_joined)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (username, email, password, date_joined))
        conn.commit()

        response = {
            "statusCode": 201,
            "body": json.dumps({
                "message": "User created successfully"
            })
        }
    except mysql.connector.Error as err:
        response = {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error connecting to the database",
                "error": str(err)
            })
        }
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return response
