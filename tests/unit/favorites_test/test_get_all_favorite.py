import json
import unittest
from unittest.mock import patch, MagicMock
from lambdas.favorites_managment.get_all_favorites_by_user.app import lambda_handler


class TestFavoritesLambdaHandler(unittest.TestCase):

    @patch('lambdas.favorites_managment.get_all_favorites_by_user.app.mysql.connector.connect')
    @patch.dict('os.environ', {
        'RDS_HOST': 'test_host',
        'RDS_USER': 'test_user',
        'RDS_PASSWORD': 'test_password',
        'RDS_DB': 'test_db'
    })
    def test_lambda_handler_success(self, mock_connect):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        # Mocking database response
        mock_cursor.fetchall.return_value = [
            (1, 'Favorite description', 'user123', 10, 'Song Title', '3:45', 1, 1, 'Rock')
        ]

        event = {
            'pathParameters': {
                'user_id': 'user123'
            }
        }

        response = lambda_handler(event, None)
        expected_body = json.dumps([{
            'favorite_id': 1,
            'description': 'Favorite description',
            'user_id': 'user123',
            'song': {
                'song_id': 10,
                'title': 'Song Title',
                'duration': '3:45',
                'album_id': 1,
                'artist_id': 1,
                'genre': 'Rock'
            }
        }])

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], expected_body)

    @patch('lambdas.favorites_managment.get_all_favorites_by_user.app.mysql.connector.connect')
    @patch.dict('os.environ', {
        'RDS_HOST': 'test_host',
        'RDS_USER': 'test_user',
        'RDS_PASSWORD': 'test_password',
        'RDS_DB': 'test_db'
    })
    def test_lambda_handler_no_favorites_found(self, mock_connect):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        # Simulate no favorites found
        mock_cursor.fetchall.return_value = []

        event = {
            'pathParameters': {
                'user_id': 'user123'
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body']), 'No favorites found for this user')

    @patch('lambdas.favorites_managment.get_all_favorites_by_user.app.mysql.connector.connect')
    @patch.dict('os.environ', {
        'RDS_HOST': 'test_host',
        'RDS_USER': 'test_user',
        'RDS_PASSWORD': 'test_password',
        'RDS_DB': 'test_db'
    })
    def test_lambda_handler_db_connection_error(self, mock_connect):
        mock_connect.side_effect = Exception("Database connection error")

        event = {
            'pathParameters': {
                'user_id': 'user123'
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Database connection error', json.loads(response['body']))

    @patch('lambdas.favorites_managment.get_all_favorites_by_user.app.mysql.connector.connect')
    @patch.dict('os.environ', {
        'RDS_HOST': 'test_host',
        'RDS_USER': 'test_user',
        'RDS_PASSWORD': 'test_password',
        'RDS_DB': 'test_db'
    })
    def test_lambda_handler_invalid_user_id(self, mock_connect):
        # Simulate case where user_id is missing
        event = {
            'pathParameters': {}
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error', json.loads(response['body']))


if __name__ == '__main__':
    unittest.main()