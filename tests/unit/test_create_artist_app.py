import unittest
import json
from unittest.mock import patch, MagicMock
import os
from mysql.connector import Error as MySQLError

from lambdas.create_artist.app import lambda_handler


class TestLambdaHandler(unittest.TestCase):

    @patch.dict(os.environ, {
        'RDS_HOST': 'testhost',
        'RDS_USER': 'testuser',
        'RDS_PASSWORD': 'testpassword',
        'RDS_DB': 'testdb'
    })
    @patch('lambdas.create_artist.app.mysql.connector.connect')
    def test_lambda_handler_success(self, mock_connect):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        event = {
            'body': json.dumps({
                'name': 'Test Artist',
                'genre': 'Pop',
                'bio': 'Test bio'
            })
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), 'Artist created successfully')

        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO artists (name, genre, bio) VALUES (%s, %s, %s)",
            ('Test Artist', 'Pop', 'Test bio')
        )
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch('lambdas.create_artist.app.mysql.connector.connect')
    def test_lambda_handler_missing_parameters(self, mock_connect):
        event = {
            'body': json.dumps({
                'name': 'Test Artist',
                'genre': 'Pop'
                # Falta 'bio'
            })
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), 'Bad request. Missing required parameters.')

    @patch('lambdas.create_artist.app.mysql.connector.connect')
    def test_lambda_handler_database_error(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        mock_cursor = MagicMock()
        mock_connection.cursor.side_effect = MySQLError("Database error")

        event = {
            'body': json.dumps({
                'name': 'Test Artist',
                'genre': 'Pop',
                'bio': 'Test bio'
            })
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Database error', json.loads(response['body']))

        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch('lambdas.create_artist.app.mysql.connector.connect')
    def test_lambda_handler_general_error(self, mock_connect):
        mock_connect.side_effect = Exception("General error")

        event = {
            'body': json.dumps({
                'name': 'Test Artist',
                'genre': 'Pop',
                'bio': 'Test bio'
            })
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('General error', json.loads(response['body']))

    if __name__ == '__main__':
        unittest.main()

