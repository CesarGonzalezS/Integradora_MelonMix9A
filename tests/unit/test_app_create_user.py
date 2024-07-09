import unittest
import json
import base64
from unittest.mock import patch, MagicMock
from pymysql import Error as MySQLError
import os

from lambdas.user_management.create_user.app import lambda_handler


class TestLambdaHandler(unittest.TestCase):

    @patch.dict(os.environ, {
        'RDS_HOST': 'testhost',
        'RDS_USER': 'testuser',
        'RDS_PASSWORD': 'testpassword',
        'RDS_DB': 'testdb'
    })
    @patch('lambdas.user_management.create_user.app.get_connection')
    def test_lambda_handler_success(self, mock_get_connection):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        # Imagen binaria simulada
        profile_image_binary = 'test_image_data'
        encoded_image = base64.b64encode(profile_image_binary.encode('utf-8')).decode('utf-8')

        event = {
            'body': json.dumps({
                'username': 'Cesargonzalea547',
                'email': 'cesargonzalea547@gmail.com',
                'password': 'Test123.',
                'date_joined': '2024-07-05',
                'profile_image_binary': profile_image_binary
            })
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 201)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Usuario creado exitosamente')

        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch('lambdas.user_management.create_user.app.get_connection')
    def test_lambda_handler_missing_parameters(self, mock_get_connection):
        # Simular una solicitud sin los parámetros obligatorios
        event = {
            'body': json.dumps({
                'username': 'Cesargonzalea547',
                'password': 'Test123.',
                'date_joined': '2024-07-05'
                # Falta profile_image_binary
            })
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Faltan parámetros obligatorios')

    @patch('lambdas.user_management.create_user.app.get_connection')
    def test_lambda_handler_invalid_email(self, mock_get_connection):
        # Simular una solicitud con correo electrónico inválido
        event = {
            'body': json.dumps({
                'username': 'Cesargonzalea547',
                'email': 'invalid-email',  # Usar un correo electrónico inválido para esta prueba
                'password': 'Test123.',
                'date_joined': '2024-07-05',
                'profile_image_binary': 'test_image_data'
            })
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Correo electrónico no válido')

    @patch('lambdas.user_management.create_user.app.get_connection')
    def test_lambda_handler_invalid_date(self, mock_get_connection):
        # Simular una solicitud con fecha de unión inválida
        event = {
            'body': json.dumps({
                'username': 'Cesargonzalea547',
                'email': 'cesargonzalea547@gmail.com',
                'password': 'Test123.',
                'date_joined': '2024-02-30',  # Fecha inválida (30 de febrero)
                'profile_image_binary': 'test_image_data'
            })
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Fecha de unión no válida')

    @patch('lambdas.user_management.create_user.app.get_connection')
    def test_lambda_handler_database_error(self, mock_get_connection):
        # Simular un error de base de datos
        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection
        mock_connection.cursor.side_effect = MySQLError('Database error')

        event = {
            'body': json.dumps({
                'username': 'Cesargonzalea547',
                'email': 'cesargonzalea547@gmail.com',
                'password': 'Test123.',
                'date_joined': '2024-07-05',
                'profile_image_binary': 'test_image_data'
            })
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)  # Ajustar el código de estado esperado a 500
        body = json.loads(response['body'])
        self.assertIn('Error de base de datos', body['message'])

        mock_connection.close.assert_called_once()

    if __name__ == '__main__':
        unittest.main()

