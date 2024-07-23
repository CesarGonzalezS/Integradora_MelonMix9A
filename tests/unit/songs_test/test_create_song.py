import unittest
from unittest.mock import patch, MagicMock
import json
import os
import mysql.connector
from mysql.connector import errorcode
import lambdas.song_management.create_song.app as lambda_function  # Adjust import path as per your actual structure

class TestLambdaHandler(unittest.TestCase):

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_successful_song_creation(self, mock_connect):
        # Setup mock for MySQL connection and cursor
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor()
        mock_connect.return_value = mock_connection

        event = {
            'body': json.dumps({
                'title': 'Test Song',
                'duration': '3:30',
                'album_id': 1,
                'artist_id': 1,
                'genre': 'Pop'
            })
        }

        context = {}

        response = lambda_function.lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), 'Song created successfully')

        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO songs (title, duration, album_id, artist_id, genre) VALUES (%s, %s, %s, %s, %s)",
            ('Test Song', '3:30', 1, 1, 'Pop')
        )
        mock_connection.commit.assert_called_once()

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_missing_parameters(self, mock_connect):
        event = {
            'body': json.dumps({
                'duration': '3:30',
                'artist_id': 1,
                'genre': 'Pop'
                # Missing title
            })
        }

        context = {}

        response = lambda_function.lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Bad request. Missing required parameters', json.loads(response['body']))

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_access_denied_error(self, mock_connect):
        # Setup mock to raise an access denied error
        mock_connect.side_effect = mysql.connector.Error(
            errno=errorcode.ER_ACCESS_DENIED_ERROR
        )

        event = {
            'body': json.dumps({
                'title': 'Test Song',
                'duration': '3:30',
                'album_id': 1,
                'artist_id': 1,
                'genre': 'Pop'
            })
        }

        context = {}

        response = lambda_function.lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body']), 'Something is wrong with your user name or password')

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_database_does_not_exist_error(self, mock_connect):
        # Setup mock to raise a database does not exist error
        mock_connect.side_effect = mysql.connector.Error(
            errno=errorcode.ER_BAD_DB_ERROR
        )

        event = {
            'body': json.dumps({
                'title': 'Test Song',
                'duration': '3:30',
                'album_id': 1,
                'artist_id': 1,
                'genre': 'Pop'
            })
        }

        context = {}

        response = lambda_function.lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body']), 'Database does not exist')

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_generic_database_error(self, mock_connect):
        # Setup mock to raise a generic database error
        mock_connect.side_effect = mysql.connector.Error(
            msg="Generic database error"
        )

        event = {
            'body': json.dumps({
                'title': 'Test Song',
                'duration': '3:30',
                'album_id': 1,
                'artist_id': 1,
                'genre': 'Pop'
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
                'title': 'Test Song',
                'duration': '3:30',
                'album_id': 1,
                'artist_id': 1,
                'genre': 'Pop'
            })
        }

        context = {}

        response = lambda_function.lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error:', json.loads(response['body']))

if __name__ == '__main__':
    unittest.main()