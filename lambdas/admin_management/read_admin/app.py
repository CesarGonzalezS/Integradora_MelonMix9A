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
        admin_id = data['admin_id']

        sql = "SELECT * FROM admin WHERE admin_id = %s"
        cursor.execute(sql, (admin_id,))
        result = cursor.fetchone()

        if result:
            admin = {
                'admin_id': result[0],
                'username': result[1],
                'email': result[2],
                'password': result[3],
                'role': result[4]
            }
            return {
                'statusCode': 200,
                'body': json.dumps(admin)
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('Admin not found')
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
