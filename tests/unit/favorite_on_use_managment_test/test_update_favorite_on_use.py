import unittest
from unittest.mock import patch, MagicMock
import json
import mysql.connector
import os
import lambdas.favorite_on_use_management.update_favorite_on_use.app as lambda_function  # Adjust import path as per your actual structure

class TestLambdaHandler(unittest.TestCase):

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_successful_update(self, mock_connect):
        # Setup mock for MySQL connection and cursor
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor()
        mock_connect.return_value = mock_connection

        event = {
            'pathParameters': {
                'favorite_on_use_id': 1
            },
            'body': json.dumps({
                'favorite_id': 2,
                'song_id': 3,
                'created_at': '2024-07-23T12:00:00Z'
            })
        }
        context = {}

        response = lambda_function.lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), 'Favorite on Use updated successfully!')

        expected_query = "UPDATE favorite_on_use SET favorite_id = %s, song_id = %s, created_at = %s WHERE favorite_on_use_id = %s"
        expected_values = (2, 3, '2024-07-23T12:00:00Z', 1)
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
            'pathParameters': {
                'favorite_on_use_id': 1
            },
            'body': json.dumps({
                'favorite_id': 2,
                'song_id': 3
                # 'created_at' is missing
            })
        }
        context = {}

        with self.assertRaises(KeyError):
            lambda_function.lambda_handler(event, context)

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_database_error(self, mock_connect):
        # Setup mock to raise a database error
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor()
        mock_cursor.execute.side_effect = mysql.connector.Error("Database error")
        mock_connect.return_value = mock_connection

        event = {
            'pathParameters': {
                'favorite_on_use_id': 1
            },
            'body': json.dumps({
                'favorite_id': 2,
                'song_id': 3,
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
            'pathParameters': {
                'favorite_on_use_id': 1
            },
            'body': json.dumps({
                'favorite_id': 2,
                'song_id': 3,
                'created_at': '2024-07-23T12:00:00Z'
            })
        }
        context = {}

        response = lambda_function.lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error:', json.loads(response['body']))

if __name__ == '__main__':
    unittest.main()