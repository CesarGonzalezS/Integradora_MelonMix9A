import unittest
import json
from unittest.mock import patch, MagicMock
import os
from mysql.connector import Error as MySQLError

from lambdas.read_all_artist.app import lambda_handler


class TestLambdaHandler(unittest.TestCase):

    @patch.dict(os.environ, {
        'RDS_HOST': 'testhost',
        'RDS_USER': 'testuser',
        'RDS_PASSWORD': 'testpassword',
        'RDS_DB': 'testdb'
    })
    @patch('lambdas.read_all_artist.app.mysql.connector.connect')
    def test_lambda_handler_success(self, mock_connect):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            (1, 'Test Artist 1', 'Pop', 'Test bio 1'),
            (2, 'Test Artist 2', 'Rock', 'Test bio 2')
        ]

        event = {}
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(len(body), 2)
        self.assertEqual(body[0]['artist_id'], 1)
        self.assertEqual(body[0]['name'], 'Test Artist 1')
        self.assertEqual(body[0]['genre'], 'Pop')
        self.assertEqual(body[0]['bio'], 'Test bio 1')

        self.assertEqual(body[1]['artist_id'], 2)
        self.assertEqual(body[1]['name'], 'Test Artist 2')
        self.assertEqual(body[1]['genre'], 'Rock')
        self.assertEqual(body[1]['bio'], 'Test bio 2')

        mock_cursor.execute.assert_called_once_with("SELECT * FROM artists")
        mock_connection.commit.assert_not_called()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch.dict(os.environ, {
        'RDS_HOST': 'testhost',
        'RDS_USER': 'testuser',
        'RDS_PASSWORD': 'testpassword',
        'RDS_DB': 'testdb'
    })
    @patch('lambdas.read_all_artist.app.mysql.connector.connect')
    def test_lambda_handler_database_error(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        mock_cursor = MagicMock()
        mock_connection.cursor.side_effect = MySQLError("Database error")

        event = {}
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Database error', json.loads(response['body']))

        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch.dict(os.environ, {
        'RDS_HOST': 'testhost',
        'RDS_USER': 'testuser',
        'RDS_PASSWORD': 'testpassword',
        'RDS_DB': 'testdb'
    })
    @patch('lambdas.read_all_artist.app.mysql.connector.connect')
    def test_lambda_handler_general_error(self, mock_connect):
        mock_connect.side_effect = Exception("General error")

        event = {}
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('General error', json.loads(response['body']))

    if __name__ == '__main__':
        unittest.main()

