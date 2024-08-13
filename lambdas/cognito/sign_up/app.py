import json
import boto3
from lambdas.cognito.sign_up.database import get_secret, get_connection

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}


def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
    except (TypeError, KeyError, json.JSONDecodeError):
        return {
            'statusCode': 400,
            'headers': headers_cors,
            'body': json.dumps({'message': 'Invalid request body.'}),
        }

    password = body.get('password')
    email = body.get('email')
    username = body.get('username')

    if not password or not email or not username:
        return {
            'statusCode': 400,
            'headers': headers_cors,
            'body': json.dumps({'message': 'Missing parameters.'})
        }

    if len(username) > 50:
        return {
            'statusCode': 400,
            'headers': headers_cors,
            'body': json.dumps({'message': 'Name exceeds 50 characters.'})
        }

    try:
        secret = get_secret()
        response = register_user(email, password, username, secret)
        return response
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers_cors,
            'body': json.dumps({'message': f'An error occurred: {str(e)}'})
        }


def register_user(email, password, username, secret):
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
            GroupName=secret['COGNITO_GROUP_NAME']
        )

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers_cors,
            'body': json.dumps({'message': f'An error occurred: {str(e)}'})
        }

    insert_into_user(email, response['UserSub'], username)

    return {
        'statusCode': 200,
        'headers': headers_cors,
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
            'headers': headers_cors,
            'body': json.dumps({'message': f'An error occurred: {str(e)}'})
        }

    finally:
        connection.close()

    return {
        'statusCode': 200,
        'headers': headers_cors,
        'body': json.dumps({'message': 'Send verification code', 'user': email})
    }
