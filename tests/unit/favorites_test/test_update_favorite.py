import unittest
from unittest.mock import patch, MagicMock
import json
import os
import mysql.connector
import lambdas.favorites_managment.update_favorite.app as lambda_function  # Adjust import path as needed

class TestUpdateFavorites(unittest.TestCase):

    @patch.dict(os.environ, {
        'RDS_HOST': 'fake_host',
        'RDS_USER': 'fake_user',
        'RDS_PASSWORD': 'fake_password',
        'RDS_DB': 'fake_db'
    })
    @patch('mysql.connector.connect')
    def test_update_favorites_success(self, mock_connect):
        # Arrange
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        favorite_id = '1'
        description = 'New description'
        user_id = 'user_1'
        created_at = '2023-07-25'
        mock_cursor.rowcount = 1

        event = {
            'body': json.dumps({
                'favorite_id': favorite_id,
                'description': description,
                'user_id': user_id,
                'created_at': created_at
            })
        }
        context = {}

        # Act
        response = lambda_function.lambda_handler(event, context)

        # Assert
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), 'favorite updated successfully')

    @patch.dict(os.environ, {
        'RDS_HOST': 'fake_host',
        'RDS_USER': 'fake_user',
        'RDS_PASSWORD': 'fake_password',
        'RDS_DB': 'fake_db'
    })
    @patch('mysql.connector.connect')
    def test_update_favorites_not_found(self, mock_connect):
        # Arrange
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        favorite_id = '1'
        description = 'New description'
        user_id = 'user_1'
        created_at = '2023-07-25'
        mock_cursor.rowcount = 0

        event = {
            'body': json.dumps({
                'favorite_id': favorite_id,
                'description': description,
                'user_id': user_id,
                'created_at': created_at
            })
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
    def test_update_favorites_bad_request(self, mock_connect):
        # Arrange
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        # Missing 'favorite_id' key
        event = {
            'body': json.dumps({
                'description': 'New description',
                'user_id': 'user_1',
                'created_at': '2023-07-25'
            })
        }
        context = {}

        # Act
        response = lambda_function.lambda_handler(event, context)

        # Assert
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), 'Bad request. Missing required parameters.')

    @patch.dict(os.environ, {
        'RDS_HOST': 'fake_host',
        'RDS_USER': 'fake_user',
        'RDS_PASSWORD': 'fake_password',
        'RDS_DB': 'fake_db'
    })
    @patch('mysql.connector.connect')
    def test_update_favorites_mysql_error(self, mock_connect):
        # Arrange
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        mock_cursor.execute.side_effect = mysql.connector.Error("MySQL error")

        favorite_id = '1'
        description = 'New description'
        user_id = 'user_1'
        created_at = '2023-07-25'

        event = {
            'body': json.dumps({
                'favorite_id': favorite_id,
                'description': description,
                'user_id': user_id,
                'created_at': created_at
            })
        }
        context = {}

        # Act
        response = lambda_function.lambda_handler(event, context)

        # Assert
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Database error: MySQL error', response['body'])

    @patch.dict(os.environ, {
        'RDS_HOST': 'fake_host',
        'RDS_USER': 'fake_user',
        'RDS_PASSWORD': 'fake_password',
        'RDS_DB': 'fake_db'
    })
    @patch('mysql.connector.connect')
    def test_update_favorites_exception(self, mock_connect):
        # Arrange
        mock_connect.side_effect = Exception("General exception")

        event = {
            'body': json.dumps({
                'favorite_id': '1',
                'description': 'New description',
                'user_id': 'user_1',
                'created_at': '2023-07-25'
            })
        }
        context = {}

        # Act
        response = lambda_function.lambda_handler(event, context)

        # Assert
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('General exception', response['body'])

if __name__ == '__main__':
    unittest.main()
