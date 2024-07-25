import unittest
from unittest.mock import patch, MagicMock
import json
import mysql.connector
import os
import lambdas.favorites_managment.create_favorite.app as lambda_function  # Adjust import path as needed

class TestLambdaHandler(unittest.TestCase):

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_successful_creation(self, mock_connect):
        # Setup mock for MySQL connection and cursor
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor()
        mock_connect.return_value = mock_connection

        event = {
            'body': json.dumps({
                'description': 'Test Favorite',
                'user_id': 123,
                'created_at': '2024-07-23T12:00:00Z'
            })
        }
        context = {}

        response = lambda_function.lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), 'favorite created successfully')

        expected_query = "INSERT INTO favorites (description , user_id , created_at) VALUES (%s, %s, %s)"
        expected_values = ('Test Favorite', 123, '2024-07-23T12:00:00Z')
        mock_cursor.execute.assert_called_once_with(expected_query, expected_values)
        mock_connection.commit.assert_called_once()

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_missing_body_fields(self, mock_connect):
        # Setup mock for MySQL connection and cursor
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor()
        mock_connect.return_value = mock_connection

        event = {
            'body': json.dumps({
                'description': 'Test Favorite',
                'user_id': 123
                # 'created_at' is missing
            })
        }
        context = {}

        response = lambda_function.lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), 'Bad request. Missing required parameters.')

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_database_error(self, mock_connect):
        # Setup mock to raise a database error
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor()
        mock_cursor.execute.side_effect = mysql.connector.Error("Database error")
        mock_connect.return_value = mock_connection

        event = {
            'body': json.dumps({
                'description': 'Test Favorite',
                'user_id': 123,
                'created_at': '2024-07-23T12:00:00Z'
            })
        }
        context = {}

        response = lambda_function.lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Database error:', json.loads(response['body']))

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_generic_error(self, mock_connect):
        # Setup mock to raise a generic error
        mock_connect.side_effect = Exception("Generic error")

        event = {
            'body': json.dumps({
                'description': 'Test Favorite',
                'user_id': 123,
                'created_at': '2024-07-23T12:00:00Z'
            })
        }
        context = {}

        response = lambda_function.lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error:', json.loads(response['body']))

if __name__ == '__main__':
    unittest.main()