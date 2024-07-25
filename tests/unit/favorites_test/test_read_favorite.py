import unittest
from unittest.mock import patch, MagicMock
import json
import os
from datetime import date
import lambdas.favorites_managment.read_favorite.app as lambda_function

class TestReadFavorites(unittest.TestCase):

    @patch.dict(os.environ, {
        'RDS_HOST': 'fake_host',
        'RDS_USER': 'fake_user',
        'RDS_PASSWORD': 'fake_password',
        'RDS_DB': 'fake_db'
    })
    @patch('mysql.connector.connect')
    def test_read_favorites_success(self, mock_connect):
        # Arrange
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        favorite_id = '1'
        favorite = (1, 'description', 'user_id', date(2023, 7, 25))
        mock_cursor.fetchone.return_value = favorite

        event = {
            'pathParameters': {
                'favorite_id': favorite_id
            }
        }
        context = {}

        # Act
        response = lambda_function.lambda_handler(event, context)

        # Assert
        self.assertEqual(response['statusCode'], 200)
        expected_body = {
            'favorite_id': favorite[0],
            'description': favorite[1],
            'user_id': favorite[2],
            'created_at': favorite[3].strftime('%Y-%m-%d')
        }
        self.assertEqual(json.loads(response['body']), expected_body)

    @patch.dict(os.environ, {
        'RDS_HOST': 'fake_host',
        'RDS_USER': 'fake_user',
        'RDS_PASSWORD': 'fake_password',
        'RDS_DB': 'fake_db'
    })
    @patch('mysql.connector.connect')
    def test_read_favorites_not_found(self, mock_connect):
        # Arrange
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        favorite_id = '1'
        mock_cursor.fetchone.return_value = None

        event = {
            'pathParameters': {
                'favorite_id': favorite_id
            }
        }
        context = {}

        # Act
        response = lambda_function.lambda_handler(event, context)

        # Assert
        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body']), 'favorite not found')

    @patch.dict(os.environ, {
        'RDS_HOST': 'fake_host',
        'RDS_USER': 'fake_user',
        'RDS_PASSWORD': 'fake_password',
        'RDS_DB': 'fake_db'
    })
    @patch('mysql.connector.connect')
    def test_read_favorites_exception(self, mock_connect):
        # Arrange
        mock_connect.side_effect = Exception("Database connection failed")

        event = {
            'pathParameters': {
                'favorite_id': '1'
            }
        }
        context = {}

        # Act
        response = lambda_function.lambda_handler(event, context)

        # Assert
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Database connection failed', response['body'])

if __name__ == '__main__':
    unittest.main()
