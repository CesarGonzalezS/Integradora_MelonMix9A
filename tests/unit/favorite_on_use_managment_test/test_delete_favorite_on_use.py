import os
import unittest
from unittest.mock import patch, MagicMock
import json
import mysql.connector
import lambdas.favorite_on_use_management.delete_favorite_on_use.app as lambda_function  # Adjust import path as per your actual structure

class TestLambdaHandler(unittest.TestCase):

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_successful_favorite_on_use_deletion(self, mock_connect):
        # Setup mock for MySQL connection and cursor
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor()
        mock_connect.return_value = mock_connection

        event = {
            'pathParameters': {
                'favorite_on_use_id': 1
            }
        }
        context = {}

        response = lambda_function.lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), 'Favorite on Use deleted successfully!')

        expected_query = "DELETE FROM favorite_on_use WHERE favorite_on_use_id = %s"
        expected_values = (1,)
        mock_cursor.execute.assert_called_once_with(expected_query, expected_values)

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_missing_parameters(self, mock_connect):
        event = {
            'pathParameters': {}
        }
        context = {}

        response = lambda_function.lambda_handler(event, context)

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_database_error(self, mock_connect):
        # Setup mock to raise a database error
        mock_connection = MagicMock()
        mock_connection.cursor.side_effect = mysql.connector.Error("Database connection error")
        mock_connect.return_value = mock_connection

        event = {
            'pathParameters': {
                'favorite_on_use_id': 1
            }
        }
        context = {}

        response = lambda_function.lambda_handler(event, context)

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_generic_error(self, mock_connect):
        # Setup mock to raise a generic error
        mock_connect.side_effect = Exception("Generic error")

        event = {
            'pathParameters': {
                'favorite_on_use_id': 1
            }
        }
        context = {}

        response = lambda_function.lambda_handler(event, context)

if __name__ == '__main__':
    unittest.main()