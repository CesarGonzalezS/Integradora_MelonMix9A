import unittest
from unittest.mock import patch, MagicMock
import json
import mysql.connector
import os
import lambdas.favorites_managment.delete_favorite.app as lambda_function  # Adjust import path as needed

class TestLambdaHandler(unittest.TestCase):

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_delete_favorite_success(self, mock_connect):
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock behavior for cursor
        mock_cursor.rowcount = 1

        event = {
            'pathParameters': {
                'favorite_id': '123'
            }
        }
        context = {}

        # Call the lambda_handler
        response = lambda_function.lambda_handler(event, context)

        # Check the result
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), 'Favorite deleted')

    @patch('mysql.connector.connect')
    def test_delete_favorite_not_found(self, mock_connect):
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock behavior for cursor
        mock_cursor.rowcount = 0

        event = {
            'pathParameters': {
                'favorite_id': '999'
            }
        }
        context = {}

        # Call the lambda_handler
        response = lambda_function.lambda_handler(event, context)

        # Check the result
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), 'Bad request. Missing required parameters.')

    @patch('mysql.connector.connect')
    def test_missing_favorite_id(self, mock_connect):
        event = {
            'pathParameters': {}
        }
        context = {}

        # Call the lambda_handler
        response = lambda_function.lambda_handler(event, context)

        # Check the result
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), 'Bad request. Missing required parameters.')

    @patch.dict(os.environ, {
        'RDS_HOST': 'fake_host',
        'RDS_USER': 'fake_user',
        'RDS_PASSWORD': 'fake_password',
        'RDS_DB': 'fake_db'
    })
    @patch('mysql.connector.connect')
    def test_lambda_handler_500_error(self, mock_connect):
        # Arrange
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.side_effect = Exception("Database connection failed")

        event = {
            'pathParameters': {
                'favorite_id': '1'
            }
        }
        context = {}

        # Act
        response = lambda_function.lambda_handler(event, context)

        # Assert
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Database connection failed', response['body'])

    @patch.dict(os.environ, {
        'RDS_HOST': 'fake_host',
        'RDS_USER': 'fake_user',
        'RDS_PASSWORD': 'fake_password',
        'RDS_DB': 'fake_db'
    })
    @patch('mysql.connector.connect')
    def test_lambda_handler_500_mysql_error(self, mock_connect):
        # Arrange
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.side_effect = mysql.connector.Error("MySQL error")

        event = {
            'pathParameters': {
                'favorite_id': '1'
            }
        }
        context = {}

        # Act
        response = lambda_function.lambda_handler(event, context)

        # Assert
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Database error: MySQL error', response['body'])

if __name__ == '__main__':
    unittest.main()