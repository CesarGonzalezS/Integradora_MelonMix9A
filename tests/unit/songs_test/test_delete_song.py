import unittest
from unittest.mock import patch, MagicMock
import json
import os
import mysql.connector
import lambdas.song_management.delete_song.app as lambda_function  # Adjust import path as per your actual structure

class TestLambdaHandler(unittest.TestCase):

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_successful_song_deletion(self, mock_connect):
        # Setup mock for MySQL connection and cursor
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor()
        mock_connect.return_value = mock_connection

        mock_cursor.rowcount = 1  # Simulate that a row was deleted

        event = {
            'pathParameters': {
                'song_id': '1'
            }
        }

        context = {}

        response = lambda_function.lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), 'Song deleted successfully')

        mock_cursor.execute.assert_called_once_with(
            "DELETE FROM songs WHERE song_id = %s",
            ('1',)
        )
        mock_connection.commit.assert_called_once()

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_song_not_found(self, mock_connect):
        # Setup mock for MySQL connection and cursor
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor()
        mock_connect.return_value = mock_connection

        mock_cursor.rowcount = 0  # Simulate that no row was found to delete

        event = {
            'pathParameters': {
                'song_id': '1'
            }
        }

        context = {}

        response = lambda_function.lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body']), 'Song not found')

        mock_cursor.execute.assert_called_once_with(
            "DELETE FROM songs WHERE song_id = %s",
            ('1',)
        )
        mock_connection.commit.assert_called_once()

    def test_missing_parameters(self):
        event = {
            # Missing pathParameters
        }

        context = {}

        response = lambda_function.lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), 'Bad request. Missing required parameters.')

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_database_error(self, mock_connect):
        # Setup mock to raise a database error
        mock_connect.side_effect = mysql.connector.Error("Database connection error")

        event = {
            'pathParameters': {
                'song_id': '1'
            }
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
                'song_id': '1'
            }
        }

        context = {}

        response = lambda_function.lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error:', json.loads(response['body']))

if __name__ == '__main__':
    unittest.main()
