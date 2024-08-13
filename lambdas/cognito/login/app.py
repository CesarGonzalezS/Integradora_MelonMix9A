import json
import boto3
from botocore.exceptions import ClientError
from lambdas.cognito.login.database import get_secret

# Define headers for CORS
headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST',
    'Access-Control-Allow-Headers': 'Content-Type'
}


def lambda_handler(event, context):
    try:
        body_parameters = parse_request_body(event)
        username = body_parameters.get('username')
        password = body_parameters.get('password')

        validate_credentials(username, password)

        secret = get_secret()
        auth_response = authenticate_user(username, password, secret)
        user_group = get_user_group(username, secret)

        return build_response(
            status_code=200,
            body={
                'id_token': auth_response['IdToken'],
                'access_token': auth_response['AccessToken'],
                'refresh_token': auth_response['RefreshToken'],
                'user_group': user_group
            }
        )

    except ValueError as ve:
        return build_response(status_code=400, body={'error_message': str(ve)})
    except ClientError as ce:
        return build_response(status_code=400, body={'error_message': ce.response['Error']['Message']})
    except Exception as e:
        return build_response(status_code=500, body={'error_message': str(e)})


def parse_request_body(event):
    """Parse and validate the request body."""
    try:
        body = json.loads(event["body"])
    except (TypeError, KeyError, json.JSONDecodeError):
        raise ValueError("Invalid request body.")
    return body


def validate_credentials(username, password):
    """Validate the presence of username and password."""
    if not username or not password:
        raise ValueError("Username and password are required.")


def authenticate_user(username, password, secret):
    """Authenticate the user and return the authentication response."""
    client = boto3.client('cognito-idp')
    try:
        response = client.admin_initiate_auth(
            UserPoolId=secret['COGNITO_USER_POOL_ID'],
            ClientId=secret['COGNITO_CLIENT_ID'],
            AuthFlow='ADMIN_USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        return response['AuthenticationResult']
    except ClientError as e:
        raise Exception(f"Error authenticating user: {str(e)}")


def get_user_group(username, secret):
    """Retrieve the user group for the specified username."""
    client = boto3.client('cognito-idp')
    try:
        response = client.admin_list_groups_for_user(
            UserPoolId=secret['COGNITO_USER_POOL_ID'],
            Username=username
        )
        return response['Groups'][0]['GroupName'] if response['Groups'] else 'User'
    except ClientError as e:
        raise Exception(f"Error retrieving user group: {str(e)}")


def build_response(status_code, body):
    """Build and return a standardized API response."""
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': json.dumps(body)
    }
