import unittest
from unittest.mock import patch, MagicMock
import json
import os
import datetime
import lambdas.albums_management.update_albums.app as lambda_function  # Adjust import path as per your actual structure

class TestLambdaHandler(unittest.TestCase):

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_successful_album_update(self, mock_connect):
        # Setup mock for MySQL connection and cursor
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor()

        # Mock data for execute() result (row updated)
        mock_cursor.rowcount = 1
        mock_connect.return_value = mock_connection

        event = {
            'body': json.dumps({
                'album_id': 1,
                'title': 'Updated Album',
                'release_date': '2024-07-15',
                'artist_id': 1
            })
        }

        context = {}

        response = lambda_function.lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), 'Album updated successfully')

        mock_cursor.execute.assert_called_once_with(
            "UPDATE albums SET title = %s, release_date = %s, artist_id = %s WHERE album_id = %s",
            ('Updated Album', '2024-07-15', 1, 1)
        )
        mock_connection.commit.assert_called_once()

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_album_not_found(self, mock_connect):
        # Setup mock for MySQL connection and cursor
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor()

        # Mock data for execute() result (no rows updated)
        mock_cursor.rowcount = 0
        mock_connect.return_value = mock_connection

        event = {
            'body': json.dumps({
                'album_id': 1,
                'title': 'Updated Album',
                'release_date': '2024-07-15',
                'artist_id': 1
            })
        }

        context = {}

        response = lambda_function.lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body']), 'Album not found')

        mock_cursor.execute.assert_called_once_with(
            "UPDATE albums SET title = %s, release_date = %s, artist_id = %s WHERE album_id = %s",
            ('Updated Album', '2024-07-15', 1, 1)
        )
        mock_connection.commit.assert_called_once()

    def test_missing_parameters(self):
        event = {
            # Missing 'body' key in event
        }

        context = {}

        response = lambda_function.lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), 'Bad request. Missing required parameters.')

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_database_error(self, mock_connect):
        # Setup mock to raise a database error
        mock_connect.side_effect = lambda_function.mysql.connector.Error("Database connection error")

        event = {
            'body': json.dumps({
                'album_id': 1,
                'title': 'Updated Album',
                'release_date': '2024-07-15',
                'artist_id': 1
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
                'album_id': 1,
                'title': 'Updated Album',
                'release_date': '2024-07-15',
                'artist_id': 1
            })
        }

        context = {}

        response = lambda_function.lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error:', json.loads(response['body']))

if __name__ == '__main__':
    unittest.main()