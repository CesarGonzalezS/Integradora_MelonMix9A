import json
import mysql.connector
import os

def lambda_handler(event, context):
    # Obtener variables de entorno
    db_host = os.environ['RDS_HOST']
    db_user = os.environ['RDS_USER']
    db_password = os.environ['RDS_PASSWORD']
    db_name = os.environ['RDS_DB']

    # Obtener datos del usuario desde la solicitud
    user_data = json.loads(event['body'])
    user_id = user_data.get('user_id')
    username = user_data.get('username')
    email = user_data.get('email')
    password = user_data.get('password')

    if not user_id or not username or not email or not password:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Missing required user data"})
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

        # Actualizar el usuario en la base de datos
        sql = "UPDATE users SET username = %s, email = %s, password = %s WHERE user_id = %s"
        val = (username, email, password, user_id)
        cursor.execute(sql, val)
        conn.commit()

        response = {
            "statusCode": 200,
            "body": json.dumps({"message": "User updated successfully"})
        }
    except mysql.connector.Error as err:
        response = {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error updating user",
                "error": str(err)
            })
        }
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return response
