import json
import mysql.connector
import os

def lambda_handler(event, context):
    # Obtener variables de entorno
    db_host = os.environ['RDS_HOST']
    db_user = os.environ['RDS_USER']
    db_password = os.environ['RDS_PASSWORD']
    db_name = os.environ['RDS_DB']

    # Obtener el ID del usuario del evento
    try:
        body = json.loads(event['body'])
        user_id = body['user_id']
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

        # Eliminar el usuario
        delete_query = "DELETE FROM users WHERE user_id = %s"
        cursor.execute(delete_query, (user_id,))
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
                    "message": "User deleted successfully"
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
