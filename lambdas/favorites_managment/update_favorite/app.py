import json
import os
import mysql.connector

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

        data = json.loads(event['body'])
        favorite_id = data['favorite_id']
        description = data['description']
        user_id = data['user_id']
        created_at = data['created_at']

        sql = "UPDATE favorites SET description = %s, user_id = %s, created_at = %s WHERE favorite_id = %s"
        cursor.execute(sql, (description, user_id, created_at, favorite_id))
        connection.commit()

        if cursor.rowcount > 0:
            return {
                'statusCode': 200,
                'body': json.dumps('favorite updated successfully')
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('favorite not found')
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
        if 'connection' in locals():
            cursor.close()
            connection.close()
