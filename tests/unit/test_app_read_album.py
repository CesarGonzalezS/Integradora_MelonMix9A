import json
import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from app import lambda_handler

class TestLambdaHandlerReadAlbum(unittest.TestCase):

    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    @patch('app.mysql.connector.connect')
    def test_lambda_handler_success(self, mock_connect):
        apigw_event = {
            'pathParameters': {
                'album_id': '1'
            }
        }

        # Mock de la conexión y cursor
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Mock del resultado de la consulta
        mock_cursor.execute.return_value = None
        mock_cursor.fetchone.return_value = (1, 'Test Album', datetime.strptime('2023-07-17', '%Y-%m-%d').date(), 1)

        response = lambda_handler(apigw_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), {
            'album_id': 1,
            'title': 'Test Album',
            'release_date': '2023-07-17',
            'artist_id': 1
        })

        mock_connect.assert_called_once_with(
            host='test_host',
            user='test_user',
            password='test_password',
            database='test_db'
        )
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM albums WHERE album_id = %s",
            ('1',)
        )
        mock_cursor.fetchone.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connect.return_value.close.assert_called_once()

    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    @patch('app.mysql.connector.connect')
    def test_lambda_handler_album_not_found(self, mock_connect):
        apigw_event = {
            'pathParameters': {
                'album_id': '1'
            }
        }

        # Mock de la conexión y cursor
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Mock del resultado de la consulta (álbum no encontrado)
        mock_cursor.execute.return_value = None
        mock_cursor.fetchone.return_value = None

        response = lambda_handler(apigw_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(response['body'], json.dumps('Album not found'))

        mock_connect.assert_called_once_with(
            host='test_host',
            user='test_user',
            password='test_password',
            database='test_db'
        )
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM albums WHERE album_id = %s",
            ('1',)
        )
        mock_cursor.fetchone.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connect.return_value.close.assert_called_once()

    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    @patch('app.mysql.connector.connect')
    def test_lambda_handler_db_error(self, mock_connect):
        apigw_event = {
            'pathParameters': {
                'album_id': '1'
            }
        }

        # Mock de la conexión que genera un error
        mock_connect.side_effect = mysql.connector.Error("Mocked DB Error")

        response = lambda_handler(apigw_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Database error', json.loads(response['body']))

        mock_connect.assert_called_once_with(
            host='test_host',
            user='test_user',
            password='test_password',
            database='test_db'
        )

    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    @patch('app.mysql.connector.connect')
    def test_lambda_handler_general_error(self, mock_connect):
        apigw_event = {
            'pathParameters': {
                'album_id': '1'
            }
        }

        # Mock de la conexión que genera un error genérico
        mock_connect.side_effect = Exception("Mocked General Error")

        response = lambda_handler(apigw_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error: Mocked General Error', json.loads(response['body']))

        mock_connect.assert_called_once_with(
            host='test_host',
            user='test_user',
            password='test_password',
            database='test_db'
        )

if __name__ == '__main__':
    unittest.main()
