import unittest
import json
from unittest.mock import patch, MagicMock
import os
from mysql.connector import Error as MySQLError

from lambdas.delete.app import lambda_handler


class TestLambdaHandler(unittest.TestCase):

    @patch.dict(os.environ, {
        'RDS_HOST': 'testhost',
        'RDS_USER': 'testuser',
        'RDS_PASSWORD': 'testpassword',
        'RDS_DB': 'testdb'
    })
    @patch('lambdas.delete.app.mysql.connector.connect')
    def test_lambda_handler_success(self, mock_connect):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        event = {
            'body': json.dumps({
                'artist_id': 123
            })
        }
        context = {}

        # Mock para simular la eliminación exitosa
        mock_cursor.rowcount = 1

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), 'Artist deleted successfully')

        mock_cursor.execute.assert_called_once_with(
            "DELETE FROM artists WHERE artist_id = %s",
            (123,)
        )
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch('lambdas.delete.app.mysql.connector.connect')
    def test_lambda_handler_artist_not_found(self, mock_connect):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        event = {
            'body': json.dumps({
                'artist_id': 456
            })
        }
        context = {}

        # Mock para simular la no existencia del artista
        mock_cursor.rowcount = 0

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body']), 'Artist not found')

        mock_cursor.execute.assert_called_once_with(
            "DELETE FROM artists WHERE artist_id = %s",
            (456,)
        )
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch('lambdas.delete.app.mysql.connector.connect')
    def test_lambda_handler_missing_parameters(self, mock_connect):
        event = {
            'body': json.dumps({
                # Falta 'artist_id'
            })
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), 'Bad request. Missing required parameters.')

    @patch('lambdas.delete.app.mysql.connector.connect')
    def test_lambda_handler_database_error(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        mock_cursor = MagicMock()
        mock_connection.cursor.side_effect = MySQLError("Database error")

        event = {
            'body': json.dumps({
                'artist_id': 789
            })
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Database error', json.loads(response['body']))

        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch('lambdas.delete.app.mysql.connector.connect')
    def test_lambda_handler_general_error(self, mock_connect):
        mock_connect.side_effect = Exception("General error")

        event = {
            'body': json.dumps({
                'artist_id': 987
            })
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('General error', json.loads(response['body']))

    if __name__ == '__main__':
        unittest.main()

