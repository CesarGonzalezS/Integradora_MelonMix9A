import unittest
from unittest.mock import patch, MagicMock
import json

import lambdas.favorites_managment.delete_favorite.app as lambda_function  # Adjust import path as needed

class TestLambdaHandler(unittest.TestCase):

    @patch('mysql.connector.connect')
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
        response = lambda_function(event, context)

        # Check the result
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), 'Favorite deleted successfully')

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
        response = lambda_handler(event, context)

        # Check the result
        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body']), 'Favorite not found')

    @patch('mysql.connector.connect')
    def test_missing_path_parameters(self, mock_connect):
        event = {}
        context = {}

        # Call the lambda_handler
        response = lambda_handler(event, context)

        # Check the result
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), 'Bad request. Missing favorite_id in path parameters.')

    @patch('mysql.connector.connect')
    def test_missing_favorite_id(self, mock_connect):
        event = {
            'pathParameters': {}
        }
        context = {}

        # Call the lambda_handler
        response = lambda_handler(event, context)

        # Check the result
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), 'Bad request. Missing favorite_id in path parameters.')

    @patch('mysql.connector.connect')
    def test_database_error(self, mock_connect):
        # Mock database connection and cursor
        mock_connect.side_effect = mysql.connector.Error("Database connection error")

        event = {
            'pathParameters': {
                'favorite_id': '123'
            }
        }
        context = {}

        # Call the lambda_handler
        response = lambda_handler(event, context)

        # Check the result
        self.assertEqual(response['statusCode'], 500)
        self.assertTrue('Database error' in json.loads(response['body']))

    @patch('mysql.connector.connect')
    def test_general_exception(self, mock_connect):
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.side_effect = Exception("General error")

        event = {
            'pathParameters': {
                'favorite_id': '123'
            }
        }
        context = {}

        # Call the lambda_handler
        response = lambda_handler(event, context)

        # Check the result
        self.assertEqual(response['statusCode'], 500)
        self.assertTrue('Error' in json.loads(response['body']))

if __name__ == '__main__':
    unittest.main()
