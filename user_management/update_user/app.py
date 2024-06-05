import json
import mysql.connector
import os

def lambda_handler(event, context):
    # Obtener variables de entorno
    db_host = os.environ['RDS_HOST']
    db_user = os.environ['RDS_USER']
    db_password = os.environ['RDS_PASSWORD']
    db_name = os.environ['RDS_DB']

    # Obtener datos del usuario del evento
    try:
        body = json.loads(event['body'])
        user_id = body['user_id']
        username = body.get('username')
        email = body.get('email')
        password = body.get('password')
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

        # Construir la consulta de actualización
        update_fields = []
        update_values = []

        if username:
            update_fields.append("username = %s")
            update_values.append(username)
        if email:
            update_fields.append("email = %s")
            update_values.append(email)
        if password:
            update_fields.append("password = %s")
            update_values.append(password)

        update_values.append(user_id)

        update_query = f"UPDATE users SET {', '.join(update_fields)} WHERE user_id = %s"
        cursor.execute(update_query, update_values)
        conn.commit()

        if cursor.rowcount == 0:
            response = {
                "statusCode": 404,
                "body": json.dumps({
                    "message": "User not found"
                })
            }
        else:
            response = {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "User updated successfully"
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
