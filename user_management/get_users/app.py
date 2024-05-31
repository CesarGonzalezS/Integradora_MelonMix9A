import json
import mysql.connector
import os

def lambda_handler(event, context):
    # Obtener variables de entorno
    db_host = os.environ['RDS_HOST']
    db_user = os.environ['RDS_USER']
    db_password = os.environ['RDS_PASSWORD']
    db_name = os.environ['RDS_DB']

    # Conectar a la base de datos RDS
    try:
        conn = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        cursor = conn.cursor(dictionary=True)

        # Obtener todos los usuarios de la base de datos
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()

        response = {
            "statusCode": 200,
            "body": json.dumps(users)
        }
    except mysql.connector.Error as err:
        response = {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error fetching users",
                "error": str(err)
            })
        }
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return response
