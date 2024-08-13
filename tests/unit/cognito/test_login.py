import json
import unittest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
from lambdas.cognito.login.app import lambda_handler, parse_request_body, validate_credentials, authenticate_user, \
    get_user_group, build_response

from lambdas.cognito.login.database import get_secret


class TestLambdaHandler(unittest.TestCase):

    @patch('lambdas.cognito.login.app.get_secret')
    @patch('lambdas.cognito.login.app.authenticate_user')
    @patch('lambdas.cognito.login.app.get_user_group')
    def test_lambda_handler_success(self, mock_get_user_group, mock_authenticate_user, mock_get_secret):
        event = {
            "body": json.dumps({
                "username": "testuser",
                "password": "testpassword"
            })
        }

        mock_get_secret.return_value = {
            'COGNITO_USER_POOL_ID': 'us-east-1_testpool',
            'COGNITO_CLIENT_ID': 'testclientid'
        }
        mock_authenticate_user.return_value = {
            'IdToken': 'test_id_token',
            'AccessToken': 'test_access_token',
            'RefreshToken': 'test_refresh_token'
        }
        mock_get_user_group.return_value = 'Admin'

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertIn('id_token', json.loads(response['body']))
        self.assertIn('access_token', json.loads(response['body']))
        self.assertIn('refresh_token', json.loads(response['body']))
        self.assertIn('user_group', json.loads(response['body']))
        self.assertEqual(json.loads(response['body'])['user_group'], 'Admin')

    @patch('lambdas.cognito.login.app.get_secret')
    @patch('lambdas.cognito.login.app.authenticate_user')
    @patch('lambdas.cognito.login.app.get_user_group')
    def test_lambda_handler_missing_credentials(self, mock_get_user_group, mock_authenticate_user, mock_get_secret):
        event = {
            "body": json.dumps({
                "username": "",
                "password": ""
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn('error_message', json.loads(response['body']))
        self.assertEqual(json.loads(response['body'])['error_message'], "Username and password are required.")

        mock_get_secret.assert_not_called()
        mock_authenticate_user.assert_not_called()
        mock_get_user_group.assert_not_called()

    def test_lambda_handler_invalid_request_body(self):
        event = {
            "body": "invalid_json"
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn('error_message', json.loads(response['body']))
        self.assertEqual(json.loads(response['body'])['error_message'], "Invalid request body.")

    @patch('lambdas.cognito.login.app.get_secret')
    @patch('lambdas.cognito.login.app.authenticate_user')
    @patch('lambdas.cognito.login.app.get_user_group')
    def test_lambda_handler_client_error(self, mock_get_user_group, mock_authenticate_user, mock_get_secret):
        event = {
            "body": json.dumps({
                "username": "testuser",
                "password": "testpassword"
            })
        }

        mock_get_secret.return_value = {
            'COGNITO_USER_POOL_ID': 'us-east-1_testpool',
            'COGNITO_CLIENT_ID': 'testclientid'
        }
        error_response = {
            'Error': {
                'Code': 'NotAuthorizedException',
                'Message': 'Incorrect username or password.'
            }
        }
        mock_authenticate_user.side_effect = ClientError(error_response, 'AdminInitiateAuth')

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn('error_message', json.loads(response['body']))
        self.assertEqual(json.loads(response['body'])['error_message'], 'Incorrect username or password.')

    @patch('lambdas.cognito.login.app.get_secret')
    @patch('lambdas.cognito.login.app.authenticate_user')
    @patch('lambdas.cognito.login.app.get_user_group')
    def test_lambda_handler_unhandled_exception(self, mock_get_user_group, mock_authenticate_user, mock_get_secret):
        event = {
            "body": json.dumps({
                "username": "testuser",
                "password": "testpassword"
            })
        }

        mock_get_secret.side_effect = Exception("Unhandled exception")

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('error_message', json.loads(response['body']))
        self.assertEqual(json.loads(response['body'])['error_message'], 'Unhandled exception')

    @patch('lambdas.cognito.login.database.boto3.session.Session.client')
    def test_get_secret(self, mock_boto3_client):
        secret_value = {"key": "value"}

        mock_client_instance = MagicMock()
        mock_client_instance.get_secret_value.return_value = {
            'SecretString': json.dumps(secret_value)
        }
        mock_boto3_client.return_value = mock_client_instance

        result = get_secret()
        self.assertEqual(result, secret_value)
if __name__ == '__main__':
    unittest.main()
