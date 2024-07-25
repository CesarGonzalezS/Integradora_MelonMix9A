import unittest
from unittest.mock import patch, MagicMock
import json
import os
import mysql.connector
import lambdas.artist_management.read_all_artist.app as lambda_function  # Adjust import path as per your actual structure

class TestLambdaHandler(unittest.TestCase):

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_successful_retrieval(self, mock_connect):
        # Setup mock for MySQL connection and cursor
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor()
        mock_connect.return_value = mock_connection

        event = {}
        context = {}

        # Sample data to be returned by the database query
        mock_cursor.fetchall.return_value = [
            (1, 'Artist One', 'Rock', 'Bio One'),
            (2, 'Artist Two', 'Pop', 'Bio Two')
        ]

        response = lambda_function.lambda_handler(event, context)

        expected_body = [
            {'artist_id': 1, 'name': 'Artist One', 'genre': 'Rock', 'bio': 'Bio One'},
            {'artist_id': 2, 'name': 'Artist Two', 'genre': 'Pop', 'bio': 'Bio Two'}
        ]

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), expected_body)

        mock_cursor.execute.assert_called_once_with("SELECT * FROM artists")

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_database_error(self, mock_connect):
        # Setup mock to raise a database error
        mock_connect.side_effect = mysql.connector.Error("Database connection error")

        event = {}
        context = {}

        response = lambda_function.lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Database error:', json.loads(response['body']))

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_generic_error(self, mock_connect):
        # Setup mock to raise a generic error
        mock_connect.side_effect = Exception("Generic error")

        event = {}
        context = {}

        response = lambda_function.lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error:', json.loads(response['body']))

if __name__ == '__main__':
    unittest.main()