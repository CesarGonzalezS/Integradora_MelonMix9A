import json
import unittest
from unittest.mock import patch, MagicMock
from lambdas.cognito.sign_up.app import lambda_handler, register_user, insert_into_user

class TestSignUpLambdaHandler(unittest.TestCase):

    @patch('lambdas.cognito.sign_up.app.get_secret')
    @patch('lambdas.cognito.sign_up.app.register_user')
    def test_lambda_handler_success(self, mock_register_user, mock_get_secret):
        event = {
            "body": json.dumps({
                "email": "testuser@example.com",
                "password": "TestPass123!",
                "username": "testuser"
            })
        }

        mock_get_secret.return_value = {
            'COGNITO_CLIENT_ID': 'testclientid',
            'COGNITO_USER_POOL_ID': 'us-east-1_testpool',
            'COGNITO_GROUP_NAME': 'UserGroup'
        }
        mock_register_user.return_value = {
            'statusCode': 200,
            'body': json.dumps({'message': 'Send verification code', 'user': 'testuserid'})
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Send verification code', json.loads(response['body'])['message'])

    def test_lambda_handler_invalid_request_body(self):
        event = {
            "body": "invalid_json"
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Invalid request body.', json.loads(response['body'])['message'])

    def test_lambda_handler_missing_parameters(self):
        event = {
            "body": json.dumps({
                "email": "testuser@example.com",
                "password": "TestPass123!"
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Missing parameters.', json.loads(response['body'])['message'])

    def test_lambda_handler_username_too_long(self):
        event = {
            "body": json.dumps({
                "email": "testuser@example.com",
                "password": "TestPass123!",
                "username": "x" * 51  # Username with 51 characters
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Name exceeds 50 characters.', json.loads(response['body'])['message'])

    @patch('lambdas.cognito.sign_up.app.get_secret')
    @patch('lambdas.cognito.sign_up.app.register_user')
    def test_lambda_handler_unhandled_exception(self, mock_register_user, mock_get_secret):
        event = {
            "body": json.dumps({
                "email": "testuser@example.com",
                "password": "TestPass123!",
                "username": "testuser"
            })
        }

        mock_get_secret.side_effect = Exception("Unhandled exception")

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('An error occurred', json.loads(response['body'])['message'])

    @patch('lambdas.cognito.sign_up.app.get_connection')
    def test_insert_into_user_success(self, mock_get_connection):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        response = insert_into_user("testuser@example.com", "testuserid", "testuser")

        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO user (email, user_id, username) VALUES (%s, %s, %s)",
            ("testuser@example.com", "testuserid", "testuser")
        )
        mock_connection.commit.assert_called_once()
        mock_connection.close.assert_called_once()

        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Send verification code', json.loads(response['body'])['message'])

    @patch('lambdas.cognito.sign_up.app.get_connection')
    def test_insert_into_user_failure(self, mock_get_connection):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.execute.side_effect = Exception("Database error")

        response = insert_into_user("testuser@example.com", "testuserid", "testuser")

        mock_connection.commit.assert_not_called()
        mock_connection.close.assert_called_once()

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('An error occurred', json.loads(response['body'])['message'])


if __name__ == '__main__':
    unittest.main()
