import unittest
from unittest.mock import patch, MagicMock
import json
import os
import mysql.connector
import lambdas.artist_management.create_artist.app as lambda_function  # Adjust import path as per your actual structure

class TestLambdaHandler(unittest.TestCase):

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_successful_artist_creation(self, mock_connect):
        # Setup mock for MySQL connection and cursor
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor()
        mock_connect.return_value = mock_connection

        event = {
            'body': json.dumps({
                'name': 'Artist Name',
                'genre': 'Pop',
                'bio': 'This is a sample bio'
            })
        }

        context = {}

        response = lambda_function.lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), 'Artist created successfully')

        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO artists (name, genre, bio) VALUES (%s, %s, %s)",
            ('Artist Name', 'Pop', 'This is a sample bio')
        )
        mock_connection.commit.assert_called_once()

    def test_missing_parameters(self):
        event = {
            'body': json.dumps({
                # Missing some parameters
                'name': 'Artist Name'
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
        mock_connect.side_effect = mysql.connector.Error("Database connection error")

        event = {
            'body': json.dumps({
                'name': 'Artist Name',
                'genre': 'Pop',
                'bio': 'This is a sample bio'
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
                'name': 'Artist Name',
                'genre': 'Pop',
                'bio': 'This is a sample bio'
            })
        }

        context = {}

        response = lambda_function.lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error:', json.loads(response['body']))

if __name__ == '__main__':
    unittest.main()