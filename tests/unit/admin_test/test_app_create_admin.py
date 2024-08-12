import unittest
from unittest.mock import patch, MagicMock
import json
import os

# Adjust the import path as needed
from lambdas.admin_management.create_admin.app import lambda_handler

class TestAdminCreate(unittest.TestCase):

    @patch('lambdas.admin_management.create_admin.app.get_secret')
    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    @patch('lambdas.admin_management.create_admin.app.boto3.client')
    def test_lambda_handler_success(self, mock_boto3_client, mock_mysql_connect, mock_get_secret):
        # Mock environment variables
        os.environ['RDS_HOST'] = 'mock_host'
        os.environ['RDS_USER'] = 'mock_user'
        os.environ['RDS_PASSWORD'] = 'mock_password'
        os.environ['RDS_DB'] = 'mock_db'

        # Mock the input event
        event = {
            'body': json.dumps({
                'username': 'test_user',
                'email': 'test@example.com',
                'password': 'TestPassword123!'
            })
        }

        # Mock boto3 client behavior
        mock_cognito_client = MagicMock()
        mock_cognito_client.sign_up.return_value = {'UserSub': 'mock_user_sub'}
        mock_boto3_client.return_value = mock_cognito_client

        # Mock get_secret
        mock_get_secret.return_value = {
            'COGNITO_CLIENT_ID': 'mock_client_id',
            'COGNITO_USER_POOL_ID': 'mock_user_pool_id'
        }

        # Mock MySQL connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_mysql_connect.return_value = mock_connection

        # Mock cursor methods if necessary
        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = []

        # Invoke the lambda_handler
        response = lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Send verification code', response['body'])

        # Assert that the user was inserted into the database
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO user (email, user_id, username) VALUES (%s, %s, %s)",
            ('test@example.com', 'mock_user_sub', 'test_user')
        )

    @patch('lambdas.admin_management.create_admin.app.get_secret')
    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    @patch('lambdas.admin_management.create_admin.app.boto3.client')
    def test_lambda_handler_missing_params(self, mock_boto3_client, mock_mysql_connect, mock_get_secret):
        # Mock environment variables
        os.environ['RDS_HOST'] = 'mock_host'
        os.environ['RDS_USER'] = 'mock_user'
        os.environ['RDS_PASSWORD'] = 'mock_password'
        os.environ['RDS_DB'] = 'mock_db'

        # Mock the input event with missing parameters
        event = {
            'body': json.dumps({
                'username': 'test_user',
                'password': 'TestPassword123!'
            })
        }

        # Invoke the lambda_handler
        response = lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Bad request. Missing required parameters.', response['body'])

    @patch('lambdas.admin_management.create_admin.app.get_secret')
    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    @patch('lambdas.admin_management.create_admin.app.boto3.client')
    def test_lambda_handler_name_exceeds_limit(self, mock_boto3_client, mock_mysql_connect, mock_get_secret):
        # Mock environment variables
        os.environ['RDS_HOST'] = 'mock_host'
        os.environ['RDS_USER'] = 'mock_user'
        os.environ['RDS_PASSWORD'] = 'mock_password'
        os.environ['RDS_DB'] = 'mock_db'

        # Mock the input event with a long username
        event = {
            'body': json.dumps({
                'username': 'a' * 51,  # 51 characters
                'email': 'test@example.com',
                'password': 'TestPassword123!'
            })
        }

        # Invoke the lambda_handler
        response = lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Name exceeds 50 characters', response['body'])

if __name__ == '__main__':
    unittest.main()