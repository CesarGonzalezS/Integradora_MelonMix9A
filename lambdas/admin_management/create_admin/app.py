import json
import os
import mysql.connector
from botocore.exceptions import ClientError
import pymysql
import boto3

headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST',
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

        data = json.loads(event['body'])
        username = data['username']
        email = data['email']
        password = data['password']

        if len(username) > 50:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'message': 'Name exceeds 50 characters.'})
            }

        if not password or not email or not username:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'message': 'Missing parameters.'})
            }

        try:
            secret = get_secret()
            response = register_admin(email, password, username, secret)
            return response
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({'message': f'An error occurred: {str(e)}'})
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


def get_secret():
    secret_name = "MelonMix_secrets"
    region_name = "us-east-2"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        secret = get_secret_value_response['SecretString']
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'An error occurred: {str(e)}')
        }

    return json.loads(secret)

def register_admin(email, password, username, secret):
    try:
        client = boto3.client('cognito-idp')
        response = client.sign_up(
            ClientId=secret['COGNITO_CLIENT_ID'],
            Username=username,
            Password=password,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email
                },
            ]
        )
        client.admin_add_user_to_group(
            UserPoolId=secret['COGNITO_USER_POOL_ID'],
            Username=username,
            GroupName='admin'
        )

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'message': f'An error occurred: {str(e)}'})
        }

    insert_into_user(email, response['UserSub'], username)

    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({'message': 'Send verification code', 'user': response['UserSub']})
    }

def insert_into_user(email, id_cognito, username):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            insert_query = "INSERT INTO user (email, user_id, username) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (email, id_cognito, username))
            connection.commit()

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'message': f'An error occurred: {str(e)}'})
        }

    finally:
        connection.close()

    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({'message': 'Send verification code', 'user': email})
    }

def get_connection():
    try:
        db_host = os.environ['RDS_HOST']
        db_user = os.environ['RDS_USER']
        db_password = os.environ['RDS_PASSWORD']
        db_name = os.environ['RDS_DB']

        connection = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Failed to connect to database: {str(e)}'
        }

    return connection

