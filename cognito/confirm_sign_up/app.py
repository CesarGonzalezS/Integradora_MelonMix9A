import json
import boto3
from database import get_secret, calculate_secret_hash
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
            'body': 'Invalid request body.'
        }

    username = body.get('username')
    confirmation_code = body.get('confirmation_code')

    try:
        secret = get_secret()
        response = confirmation_registration(username, confirmation_code, secret)
        return response
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers_cors,
            'body': json.dumps(f'An error occurred: {str(e)}')
        }


def confirmation_registration(username, confirmation_code, secret):
    try:
        client = boto3.client('cognito-idp')
        client.confirm_sign_up(
            ClientId=secret['COGNITO_CLIENT_ID'],
            Username=username,
            ConfirmationCode=confirmation_code,
        )

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'An error occurred: {str(e)}')
        }

    return {
        'statusCode': 200,
        'headers': headers_cors,
        'body': json.dumps({'message': 'User confirmed'})
    }
