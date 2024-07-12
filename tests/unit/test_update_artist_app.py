import unittest
import json
from unittest.mock import patch, MagicMock
import os
from mysql.connector import Error as MySQLError

from lambdas.update_artist.app import lambda_handler


class TestLambdaHandler(unittest.TestCase):

    @patch.dict(os.environ, {
        'RDS_HOST': 'testhost',
        'RDS_USER': 'testuser',
        'RDS_PASSWORD': 'testpassword',
        'RDS_DB': 'testdb'
    })
    @patch('lambdas.update_artist.app.mysql.connector.connect')
    def test_lambda_handler_success(self, mock_connect):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        event = {
            'body': json.dumps({
                'artist_id': 1,
                'name': 'Updated Artist',
                'genre': 'Rock',
                'bio': 'Updated bio'
            })
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], json.dumps('Artist updated successfully'))

        mock_cursor.execute.assert_called_once_with(
            "UPDATE artists SET name = %s, genre = %s, bio = %s WHERE artist_id = %s",
            ('Updated Artist', 'Rock', 'Updated bio', 1)
        )
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch.dict(os.environ, {
        'RDS_HOST': 'testhost',
        'RDS_USER': 'testuser',
        'RDS_PASSWORD': 'testpassword',
        'RDS_DB': 'testdb'
    })
    @patch('lambdas.update_artist.app.mysql.connector.connect')
    def test_lambda_handler_no_fields_to_update(self, mock_connect):
        event = {
            'body': json.dumps({
                'artist_id': 1
                # No se proporcionan campos para actualizar
            })
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(response['body'], json.dumps('Bad request. No fields to update.'))

        mock_connect.assert_not_called()

    @patch.dict(os.environ, {
        'RDS_HOST': 'testhost',
        'RDS_USER': 'testuser',
        'RDS_PASSWORD': 'testpassword',
        'RDS_DB': 'testdb'
    })
    @patch('lambdas.update_artist.app.mysql.connector.connect')
    def test_lambda_handler_missing_parameters(self, mock_connect):
        event = {
            'body': json.dumps({
                # Faltan parámetros obligatorios como artist_id
            })
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(response['body'], json.dumps('Bad request. Missing required parameters.'))

        mock_connect.assert_not_called()

    @patch.dict(os.environ, {
        'RDS_HOST': 'testhost',
        'RDS_USER': 'testuser',
        'RDS_PASSWORD': 'testpassword',
        'RDS_DB': 'testdb'
    })
    @patch('lambdas.update_artist.app.mysql.connector.connect')
    def test_lambda_handler_database_error(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        mock_cursor = MagicMock()
        mock_connection.cursor.side_effect = MySQLError("Database error")

        event = {
            'body': json.dumps({
                'artist_id': 1,
                'name': 'Updated Artist',
                'genre': 'Rock',
                'bio': 'Updated bio'
            })
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
    @patch('lambdas.update_artist.app.mysql.connector.connect')
    def test_lambda_handler_general_error(self, mock_connect):
        mock_connect.side_effect = Exception("General error")

        event = {
            'body': json.dumps({
                'artist_id': 1,
                'name': 'Updated Artist',
                'genre': 'Rock',
                'bio': 'Updated bio'
            })
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('General error', json.loads(response['body']))

    if __name__ == '__main__':
        unittest.main()

