import json
import os
import mysql.connector

headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type'
}

def lambda_handler(event, context):
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

        cursor = connection.cursor()

        artist_id = event['pathParameters']['artist_id']

        sql = "SELECT * FROM artists WHERE artist_id = %s"
        cursor.execute(sql, (artist_id,))
        result = cursor.fetchone()

        if result:
            # Convertir la fecha a cadena de texto antes de serializar a JSON, si existe
            artist = {
                'artist_id': result[0],
                'name': result[1],
                'genre': result[2],
                'bio': result[3]
            }
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(artist)
            }
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps('Artist not found')
            }
    except KeyError:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps('Bad request. Missing required parameters.')
        }
    except mysql.connector.Error as err:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps(f"Database error: {str(err)}")
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps(f"Error: {str(e)}")
        }
    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()
