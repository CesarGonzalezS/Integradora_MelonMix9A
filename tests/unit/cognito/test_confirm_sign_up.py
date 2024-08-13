import json
import unittest
from unittest.mock import patch, MagicMock
from lambdas.cognito.confirm_sign_up.database import get_secret

from lambdas.cognito.confirm_sign_up.app import lambda_handler, confirmation_registration

headers_cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}
class TestLambdaHandler(unittest.TestCase):

    @patch('lambdas.cognito.confirm_sign_up.app.get_secret')
    @patch('lambdas.cognito.confirm_sign_up.app.confirmation_registration')
    def test_lambda_handler_success(self, mock_confirmation_registration, mock_get_secret):
        event = {
            'body': json.dumps({'username': 'test_user', 'confirmation_code': '123456'})
        }

        mock_get_secret.return_value = {
            'COGNITO_CLIENT_ID': 'dummy_client_id'
        }
        mock_confirmation_registration.return_value = {
            'statusCode': 200,
            'headers': headers_cors,
            'body': json.dumps({'message': 'User confirmed'})
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertIn('User confirmed', json.loads(response['body'])['message'])

        mock_get_secret.assert_called_once()
        mock_confirmation_registration.assert_called_once_with('test_user', '123456', mock_get_secret.return_value)

    def test_lambda_handler_invalid_request_body(self):
        event = {
            'body': 'invalid_json'
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Invalid request body.', response['body'])

    @patch('lambdas.cognito.confirm_sign_up.app.get_secret')
    @patch('lambdas.cognito.confirm_sign_up.app.confirmation_registration')
    def test_lambda_handler_internal_error(self, mock_confirmation_registration, mock_get_secret):
        event = {
            'body': json.dumps({'username': 'test_user', 'confirmation_code': '123456'})
        }

        mock_get_secret.side_effect = Exception('Secret retrieval error')

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('An error occurred', json.loads(response['body']))

        mock_get_secret.assert_called_once()
        mock_confirmation_registration.assert_not_called()

    @patch('lambdas.cognito.confirm_sign_up.app.boto3.client')
    def test_confirmation_registration_success(self, mock_boto_client):
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client

        secret = {'COGNITO_CLIENT_ID': 'dummy_client_id'}
        response = confirmation_registration('test_user', '123456', secret)

        self.assertEqual(response['statusCode'], 200)
        self.assertIn('User confirmed', json.loads(response['body'])['message'])

        mock_client.confirm_sign_up.assert_called_once_with(
            ClientId='dummy_client_id',
            Username='test_user',
            ConfirmationCode='123456',
        )

    @patch('lambdas.cognito.confirm_sign_up.app.boto3.client')
    def test_confirmation_registration_error(self, mock_boto_client):
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client

        mock_client.confirm_sign_up.side_effect = Exception('Cognito error')

        secret = {'COGNITO_CLIENT_ID': 'dummy_client_id'}
        response = confirmation_registration('test_user', '123456', secret)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('An error occurred', json.loads(response['body']))

        mock_client.confirm_sign_up.assert_called_once_with(
            ClientId='dummy_client_id',
            Username='test_user',
            ConfirmationCode='123456',
        )

    @patch('lambdas.cognito.confirm_sign_up.database.boto3.client')
    def test_get_secret(self, mock_boto3_client):
        # Mock boto3 client behavior
        mock_secrets_client = MagicMock()
        mock_secrets_client.get_secret_value.return_value = {
            'SecretString': '{"COGNITO_CLIENT_ID": "mock_client_id", "COGNITO_USER_POOL_ID": "mock_user_pool_id"}'
        }
        mock_boto3_client.return_value = mock_secrets_client

        # Invoke the get_secret function
        secret = get_secret()

        # Assertions
        self.assertEqual(secret['COGNITO_CLIENT_ID'], '48qsbjmtu76mrv90ndrq1hfvop')
        self.assertEqual(secret['COGNITO_USER_POOL_ID'], 'us-east-2_nB20FTJg4')



if __name__ == '__main__':
    unittest.main()