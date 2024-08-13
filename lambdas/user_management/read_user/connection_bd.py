import pymysql
import os
import logging
from lambdas.user_management.read_user.get_secrets import get_secret

logging.basicConfig(level=logging.INFO)


def connect_to_db():
    try:
        secrets = get_secret(os.getenv('SECRET_NAME'), os.getenv('REGION_NAME'))
        connection = pymysql.connect(
            host=secrets['host'],
            user=secrets['username'],
            password=secrets['password'],
            database=os.getenv('RDS_DB')
        )
        logging.info("Connection established successfully.")
        return connection
    except Exception as e:
        logging.error("Error connecting to the database: %s", e)
        raise e


def execute_query(connection, query):
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
    except Exception as e:
        logging.error("Error executing query: %s", e)
        raise e


def close_connection(connection):
    try:
        if connection:
            connection.close()
            logging.info("Connection closed successfully.")
    except Exception as e:
        logging.error("Error closing connection: %s", e)
        raise e
