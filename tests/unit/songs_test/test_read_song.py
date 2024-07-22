import unittest
from unittest.mock import patch, MagicMock
import json
import os
import datetime
import lambdas.song_management.read_song.app as lambda_function  # Adjust import path as per your actual structure

class TestLambdaHandler(unittest.TestCase):

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_successful_song_read(self, mock_connect):
        # Setup mock for MySQL connection and cursor
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor()

        # Mock data for fetchone() result
        mock_cursor.fetchone.return_value = (
            1, 'Test Song', '3:30', 1, 1, 'Pop'
        )
        mock_connect.return_value = mock_connection

        event = {
            'pathParameters': {
                'song_id': '1'
            }
        }

        context = {}

        response = lambda_function.lambda_handler(event, context)

        expected_body = {
            'song_id': 1,
            'title': 'Test Song',
            'duration': '3:30',
            'album_id': 1,
            'artist_id': 1,
            'genre': 'Pop'
        }

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), expected_body)

        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM songs WHERE song_id = %s",
            ('1',)
        )

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_song_not_found(self, mock_connect):
        # Setup mock for MySQL connection and cursor
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor()

        # Mock data for fetchone() result
        mock_cursor.fetchone.return_value = None
        mock_connect.return_value = mock_connection

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
            "SELECT * FROM songs WHERE song_id = %s",
            ('1',)
        )

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