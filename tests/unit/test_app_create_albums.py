import json
import os
import unittest
from unittest.mock import patch, MagicMock
from lambdas.album_management.create_album.app import lambda_handler

class TestLambdaHandler(unittest.TestCase):

    @patch("lambdas.album_management.create_album.app.get_secret")
    @patch("lambdas.album_management.create_album.app.connect_to_db")
    @patch("lambdas.album_management.create_album.app.execute_query")
    @patch("lambdas.album_management.create_album.app.close_connection")
    def test_lambda_handler_success(self, mock_close, mock_execute, mock_connect, mock_get_secret):
        apigw_event = {
            'body': '{"title": "Test Album", "release_date": "2024-01-01", "artist_id": 1}'
        }

        mock_get_secret.return_value = {
            'host': 'test_host',
            'username': 'test_user',
            'password': 'test_pass'
        }
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        response = lambda_handler(apigw_event, None)

        self.assertEqual(response['statusCode'], 201)
        self.assertEqual(json.loads(response['body']), {'message': 'Álbum creado exitosamente'})

        mock_get_secret.assert_called_once_with(os.getenv('SECRET_NAME'), os.getenv('REGION_NAME'))
        mock_connect.assert_called_once_with('test_host', 'test_user', 'test_pass', os.getenv('RDS_DB'))
        mock_execute.assert_called_once_with(
            mock_connection,
            "INSERT INTO albums (title, release_date, artist_id) VALUES (%s, %s, %s)",
            ('Test Album', '2024-01-01', 1)
        )
        mock_close.assert_called_once_with(mock_connection)

    def test_lambda_handler_missing_parameters(self):
        apigw_event = {
            'body': '{"title": "Test Album"}'
        }

        response = lambda_handler(apigw_event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), {'message': 'Faltan parámetros obligatorios'})

    @patch("lambdas.album_management.create_album.app.get_secret")
    @patch("lambdas.album_management.create_album.app.connect_to_db")
    def test_lambda_handler_db_error(self, mock_connect, mock_get_secret):
        apigw_event = {
            'body': '{"title": "Test Album", "release_date": "2024-01-01", "artist_id": 1}'
        }

        mock_get_secret.return_value = {
            'host': 'test_host',
            'username': 'test_user',
            'password': 'test_pass'
        }
        mock_connect.side_effect = mysql.connector.Error("DB connection error")

        response = lambda_handler(apigw_event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error en la base de datos', json.loads(response['body']))

    @patch("lambdas.album_management.create_album.app.get_secret")
    @patch("lambdas.album_management.create_album.app.connect_to_db")
    def test_lambda_handler_general_error(self, mock_connect, mock_get_secret):
        apigw_event = {
            'body': '{"title": "Test Album", "release_date": "2024-01-01", "artist_id": 1}'
        }

        mock_get_secret.return_value = {
            'host': 'test_host',
            'username': 'test_user',
            'password': 'test_pass'
        }
        mock_connect.side_effect = Exception("General error")

        response = lambda_handler(apigw_event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error interno del servidor', json.loads(response['body']))

if __name__ == '__main__':
    unittest.main()