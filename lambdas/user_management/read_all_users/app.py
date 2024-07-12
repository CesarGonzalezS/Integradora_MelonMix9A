import json
import os
import logging
from connection_bd import connect_to_db, execute_query, close_connection
from get_secrets import get_secret

logging.basicConfig(level=logging.INFO)


def lambda_handler(event, context):
    try:
        # Obtener secretos de AWS Secrets Manager
        db_secret_name = os.environ['DB_SECRET_NAME']
        region_name = os.environ['REGION_NAME']
        db_secret = get_secret(db_secret_name, region_name)

        # Conectar a la base de datos
        connection = connect_to_db(db_secret['host'], db_secret['username'], db_secret['password'], db_secret['dbname'])

        # Ejecutar consulta SQL
        sql = "SELECT * FROM users"
        results = execute_query(connection, sql)

        # Procesar resultados
        users = []
        for user in results:
            user_dict = {
                'user_id': user[0],
                'username': user[1],
                'email': user[2],
                'password': user[3],
                'date_joined': user[4].strftime('%Y-%m-%d')
            }
            users.append(user_dict)

        return {
            'statusCode': 200,
            'body': json.dumps(users)
        }
    except Exception as e:
        logging.error(f"Error in lambda_handler: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }
    finally:
        if 'connection' in locals():
            close_connection(connection)
