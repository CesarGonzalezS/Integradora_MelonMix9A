import json
import unittest
from unittest.mock import patch, MagicMock
from lambdas.user_management.read_user.app import lambda_handler


class TestLambdaHandler(unittest.TestCase):

    @patch("lambdas.user_management.read_user.app.read_users")
    def test_lambda_handler_success(self, mock_read_users):
        mock_read_users.return_value = [
            {'user_id': 1, 'username': 'testuser', 'email': 'test@example.com', 'password': 'hashedpassword',
             'date_joined': '2022-01-01'}
        ]

        response = lambda_handler({'username': 'testuser'}, {})

        self.assertEqual(response['statusCode'], 200)
        self.assertIn('testuser', response['body'])

    @patch("lambdas.user_management.read_user.app.read_users")
    def test_lambda_handler_db_connection_error(self, mock_read_users):
        mock_read_users.side_effect = Exception("DB connection error")

        response = lambda_handler({'username': 'testuser'}, {})

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('DB connection error', response['body'])

    @patch("lambdas.user_management.read_user.app.read_users")
    def test_lambda_handler_query_error(self, mock_read_users):
        mock_read_users.side_effect = Exception("Query execution error")

        response = lambda_handler({'username': 'testuser'}, {})

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Query execution error', response['body'])

    @patch("lambdas.user_management.read_user.app.read_users")
    def test_lambda_handler_secret_manager_error(self, mock_get_secret):
        mock_get_secret.side_effect = Exception("Secrets Manager error")

        response = lambda_handler({'username': 'testuser'}, {})

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Secrets Manager error', response['body'])


if __name__ == '__main__':
    unittest.main()
