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

    if not user_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Missing required user_id"})
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

        # Eliminar el usuario de la base de datos
        sql = "DELETE FROM users WHERE user_id = %s"
        val = (user_id,)
        cursor.execute(sql, val)
        conn.commit()

        response = {
            "statusCode": 200,
            "body": json.dumps({"message": "User deleted successfully"})
        }
    except mysql.connector.Error as err:
        response = {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error deleting user",
                "error": str(err)
            })
        }
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return response
