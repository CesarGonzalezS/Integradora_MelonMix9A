import json
import os
import mysql.connector

# Función para establecer la conexión a la base de datos
def get_database_connection():
    db_host = os.environ['RDS_HOST']
    db_user = os.environ['RDS_USER']
    db_password = os.environ['RDS_PASSWORD']
    db_name = os.environ['RDS_DB']

    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

# Función para ejecutar una consulta SQL
def execute_sql(connection, sql, params):
    cursor = connection.cursor()
    cursor.execute(sql, params)
    connection.commit()
    return cursor
def lambda_handler(event, context):
    try:
        # Validar y obtener los datos del evento
        data = json.loads(event['body'])
        user_id = data.get('user_id')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        date_joined = data.get('date_joined')

        if not user_id or not username or not email or not password or not date_joined:
            return {
                'statusCode': 400,
                'body': json.dumps('Bad request. Missing required parameters.')
            }

        # Establecer conexión a la base de datos
        connection = get_database_connection()

        # Obtener cursor para ejecutar consultas
        cursor = connection.cursor()

        # Ejecutar la actualización en la base de datos
        sql = "UPDATE users SET username = %s, email = %s, password = %s, date_joined = %s WHERE user_id = %s"
        execute_sql(connection, sql, (username, email, password, date_joined, user_id))

        # Verificar si se actualizó correctamente
        if cursor.rowcount > 0:
            return {
                'statusCode': 200,
                'body': json.dumps('User updated successfully')
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('User not found')
            }
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps('Bad request. Missing required parameters.')
        }
    except mysql.connector.Error as err:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Database error: {str(err)}")
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
