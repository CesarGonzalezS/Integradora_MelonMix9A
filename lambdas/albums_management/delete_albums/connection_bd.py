import pymysql
import logging

logging.basicConfig(level=logging.INFO)

def connect_to_db(host, user, password, database):
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        logging.info("Connection established successfully.")
        return connection
    except Exception as e:
        logging.error("Error connecting to the database: %s", e)
        raise e

def execute_query(connection, query, params):
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            connection.commit()
            return True
    except Exception as e:
        logging.error("Error executing query: %s", e)
        connection.rollback()
        raise e

def close_connection(connection):
    try:
        if connection:
            connection.close()
            logging.info("Connection closed successfully.")
    except Exception as e:
        logging.error("Error closing connection: %s", e)
        raise e