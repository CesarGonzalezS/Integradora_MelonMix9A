import json
import os
import unittest
from unittest.mock import patch, MagicMock
from lambdas.user_management.create_user.app import lambda_handler

class TestLambdaHandler(unittest.TestCase):

    @patch("lambdas.user_management.create_user.app.get_secret")
    @patch("lambdas.user_management.create_user.app.connect_to_db")
    @patch("lambdas.user_management.create_user.app.close_connection")
    def test_lambda_handler_success(self, mock_close_connection, mock_connect_to_db, mock_get_secret):
        apigw_event = {
            'body': '{"username": "testuser", "email": "testuser@example.com", "password": "password123", "date_joined": "2023-07-08", "profile_image_binary": "aGVsbG8gd29ybGQ="}'
        }

        mock_connection = MagicMock()
        mock_connect_to_db.return_value = mock_connection
        mock_get_secret.return_value = {
            "host": "mock_host",
            "username": "mock_user",
            "password": "mock_password"
        }

        response = lambda_handler(apigw_event, None)

        self.assertEqual(response['statusCode'], 201)
        self.assertEqual(json.loads(response['body'])['message'], 'Usuario creado exitosamente')

        mock_get_secret.assert_called_once()
        mock_connect_to_db.assert_called_once_with("mock_host", "mock_user", "mock_password", os.getenv('RDS_DB'))
        mock_close_connection.assert_called_once_with(mock_connection)

    @patch("lambdas.user_management.create_user.app.get_secret")
    @patch("lambdas.user_management.create_user.app.connect_to_db")
    @patch("lambdas.user_management.create_user.app.close_connection")
    def test_lambda_handler_missing_parameters(self, mock_close_connection, mock_connect_to_db, mock_get_secret):
        apigw_event = {
            'body': '{"username": "testuser", "email": "", "password": "password123", "date_joined": "2023-07-08", "profile_image_binary": "aGVsbG8gd29ybGQ="}'
        }

        response = lambda_handler(apigw_event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], 'Faltan parámetros obligatorios')

        mock_get_secret.assert_not_called()
        mock_connect_to_db.assert_not_called()
        mock_close_connection.assert_not_called()

    @patch("lambdas.user_management.create_user.app.get_secret")
    @patch("lambdas.user_management.create_user.app.connect_to_db")
    @patch("lambdas.user_management.create_user.app.close_connection")
    def test_lambda_handler_invalid_email(self, mock_close_connection, mock_connect_to_db, mock_get_secret):
        apigw_event = {
            'body': '{"username": "testuser", "email": "invalid_email", "password": "password123", "date_joined": "2023-07-08", "profile_image_binary": "aGVsbG8gd29ybGQ="}'
        }

        response = lambda_handler(apigw_event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], 'Correo electrónico no válido')

        mock_get_secret.assert_not_called()
        mock_connect_to_db.assert_not_called()
        mock_close_connection.assert_not_called()

    @patch("lambdas.user_management.create_user.app.get_secret")
    @patch("lambdas.user_management.create_user.app.connect_to_db")
    @patch("lambdas.user_management.create_user.app.close_connection")
    def test_lambda_handler_invalid_date(self, mock_close_connection, mock_connect_to_db, mock_get_secret):
        apigw_event = {
            'body': '{"username": "testuser", "email": "testuser@example.com", "password": "password123", "date_joined": "invalid_date", "profile_image_binary": "aGVsbG8gd29ybGQ="}'
        }

        response = lambda_handler(apigw_event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], 'Fecha de unión no válida')

        mock_get_secret.assert_not_called()
        mock_connect_to_db.assert_not_called()
        mock_close_connection.assert_not_called()

    @patch("lambdas.user_management.create_user.app.get_secret")
    @patch("lambdas.user_management.create_user.app.connect_to_db")
    @patch("lambdas.user_management.create_user.app.close_connection")
    def test_lambda_handler_encoding_error(self, mock_close_connection, mock_connect_to_db, mock_get_secret):
        apigw_event = {
            'body': '{"username": "testuser", "email": "testuser@example.com", "password": "password123", "date_joined": "2023-07-08", "profile_image_binary": "invalid_binary"}'
        }

        response = lambda_handler(apigw_event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Error al codificar la imagen a base64', json.loads(response['body'])['message'])

        mock_get_secret.assert_not_called()
        mock_connect_to_db.assert_not_called()
        mock_close_connection.assert_not_called()

    @patch("lambdas.user_management.create_user.app.get_secret")
    @patch("lambdas.user_management.create_user.app.connect_to_db")
    @patch("lambdas.user_management.create_user.app.close_connection")
    def test_lambda_handler_secret_manager_error(self, mock_close_connection, mock_connect_to_db, mock_get_secret):
        apigw_event = {
            'body': '{"username": "testuser", "email": "testuser@example.com", "password": "password123", "date_joined": "2023-07-08", "profile_image_binary": "aGVsbG8gd29ybGQ="}'
        }

        mock_get_secret.side_effect = Exception("Secret Manager Error")

        response = lambda_handler(apigw_event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body'])['message'], 'Error interno del servidor')

        mock_get_secret.assert_called_once()
        mock_connect_to_db.assert_not_called()
        mock_close_connection.assert_not_called()

    @patch("lambdas.user_management.create_user.app.get_secret")
    @patch("lambdas.user_management.create_user.app.connect_to_db")
    @patch("lambdas.user_management.create_user.app.close_connection")
    def test_lambda_handler_db_connection_error(self, mock_close_connection, mock_connect_to_db, mock_get_secret):
        apigw_event = {
            'body': '{"username": "testuser", "email": "testuser@example.com", "password": "password123", "date_joined": "2023-07-08", "profile_image_binary": "aGVsbG8gd29ybGQ="}'
        }

        mock_get_secret.return_value = {
            "host": "mock_host",
            "username": "mock_user",
            "password": "mock_password"
        }
        mock_connect_to_db.side_effect = Exception("DB Connection Error")

        response = lambda_handler(apigw_event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body'])['message'], 'Error interno del servidor')

        mock_get_secret.assert_called_once()
        mock_connect_to_db.assert_called_once_with("mock_host", "mock_user", "mock_password", os.getenv('RDS_DB'))
        mock_close_connection.assert_not_called()

if __name__ == '__main__':
    unittest.main()
