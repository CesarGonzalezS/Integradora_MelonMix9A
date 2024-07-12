import unittest
import json
from unittest.mock import patch, MagicMock
import os
from mysql.connector import Error as MySQLError

from lambdas.read_artist.app import lambda_handler


class TestLambdaHandler(unittest.TestCase):

    @patch.dict(os.environ, {
        'RDS_HOST': 'testhost',
        'RDS_USER': 'testuser',
        'RDS_PASSWORD': 'testpassword',
        'RDS_DB': 'testdb'
    })
    @patch('lambdas.read_artist.app.mysql.connector.connect')
    def test_lambda_handler_success(self, mock_connect):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = (1, 'Test Artist', 'Pop', 'Test bio')

        event = {
            'body': json.dumps({'artist_id': 1})
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['artist_id'], 1)
        self.assertEqual(body['name'], 'Test Artist')
        self.assertEqual(body['genre'], 'Pop')
        self.assertEqual(body['bio'], 'Test bio')

        mock_cursor.execute.assert_called_once_with("SELECT * FROM artists WHERE artist_id = %s", (1,))
        mock_connection.commit.assert_not_called()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch.dict(os.environ, {
        'RDS_HOST': 'testhost',
        'RDS_USER': 'testuser',
        'RDS_PASSWORD': 'testpassword',
        'RDS_DB': 'testdb'
    })
    @patch('lambdas.read_artist.app.mysql.connector.connect')
    def test_lambda_handler_artist_not_found(self, mock_connect):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = None

        event = {
            'body': json.dumps({'artist_id': 999})  # Simular un ID que no existe
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(response['body'], json.dumps('Artist not found'))

        mock_cursor.execute.assert_called_once_with("SELECT * FROM artists WHERE artist_id = %s", (999,))
        mock_connection.commit.assert_not_called()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch.dict(os.environ, {
        'RDS_HOST': 'testhost',
        'RDS_USER': 'testuser',
        'RDS_PASSWORD': 'testpassword',
        'RDS_DB': 'testdb'
    })
    @patch('lambdas.read_artist.app.mysql.connector.connect')
    def test_lambda_handler_database_error(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        mock_cursor = MagicMock()
        mock_connection.cursor.side_effect = MySQLError("Database error")

        event = {
            'body': json.dumps({'artist_id': 1})
        }
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
    @patch('lambdas.read_artist.app.mysql.connector.connect')
    def test_lambda_handler_general_error(self, mock_connect):
        mock_connect.side_effect = Exception("General error")

        event = {
            'body': json.dumps({'artist_id': 1})
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('General error', json.loads(response['body']))

    if __name__ == '__main__':
        unittest.main()

