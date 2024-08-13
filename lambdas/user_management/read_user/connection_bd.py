import mysql.connector
import os
import logging

logging.basicConfig(level=logging.INFO)


def connect_to_db():
    try:
        db_host = os.environ['RDS_HOST']
        db_user = os.environ['RDS_USER']
        db_password = os.environ['RDS_PASSWORD']
        db_name = os.environ['RDS_DB']

        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
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
