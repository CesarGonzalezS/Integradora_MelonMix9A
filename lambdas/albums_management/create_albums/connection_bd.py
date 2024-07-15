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

def execute_query(connection, query, params=None):


    try:
        with connection.cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            connection.commit()
            return cursor.rowcount  # Devuelve el número de filas afectadas
    except Exception as e:
        connection.rollback()
        logging.error("Error executing query: %s", e)
        raise e

def close_connection(connection):
    """
    Cierra la conexión a la base de datos MySQL.

    Args:
        connection (Connection): La conexión a la base de datos.
    """
    try:
        connection.close()
        logging.info("Connection closed successfully.")
    except Exception as e:
        logging.error("Error closing connection: %s", e)
        raise e
