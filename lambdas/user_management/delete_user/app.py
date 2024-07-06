import json
import os
from pymysql import connect, Error as MySQLError
def get_connection():
    return connect(
        host=os.environ['RDS_HOST'],
        user=os.environ['RDS_USER'],
        password=os.environ['RDS_PASSWORD'],
        database=os.environ['RDS_DB']
    )

def lambda_handler(event, context):
    connection = None
    try:
        body = json.loads(event['body'])
        user_id = body.get('user_id')

        # Validación de parámetros obligatorios
        if not user_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Faltan parámetros obligatorios'})
            }

        # Eliminación de usuario en la base de datos
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                sql = "DELETE FROM users WHERE user_id = %s"
                cursor.execute(sql, (user_id,))
            connection.commit()

            if cursor.rowcount > 0:
                return {
                    'statusCode': 200,
                    'body': json.dumps({'message': 'Usuario eliminado exitosamente'})
                }
            else:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'message': 'Usuario no encontrado'})
                }
        except MySQLError as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'Error de base de datos: ' + str(e)})
            }
        finally:
            if connection:
                connection.close()

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error interno del servidor: ' + str(e)})
        }