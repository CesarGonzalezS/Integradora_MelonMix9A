import unittest
from unittest.mock import patch, MagicMock
import os
import json
from datetime import date

from lambdas.user_management.read_user.app import lambda_handler


class TestLambdaHandler(unittest.TestCase):

    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password',
                             'RDS_DB': 'test_db'})
    @patch('mysql.connector.connect')
    def test_lambda_handler_success(self, mock_connect):
        # Mock de la conexión y cursor
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Mock de la consulta y resultados
        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = [
            (1, 'test_user', 'test@example.com', 'password', date(2024, 7, 8), 'base64encodedimage')
        ]

        # Ejecutar la lambda handler
        event = {}
        context = {}
        response = lambda_handler(event, context)

        # Verificar el resultado
        self.assertEqual(response['statusCode'], 200)
        users = json.loads(response['body'])
        self.assertIsInstance(users, list)
        self.assertEqual(users[0]['user_id'], 1)
        self.assertEqual(users[0]['profile_image_base64'], 'base64encodedimage')

    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password',
                             'RDS_DB': 'test_db'})
    @patch('mysql.connector.connect')
    def test_lambda_handler_user_not_found(self, mock_connect):
        # Mock de la conexión y cursor
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Mock de la consulta y resultados (usuario no encontrado)
        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = []

        # Ejecutar la lambda handler
        event = {}
        context = {}
        response = lambda_handler(event, context)

        # Verificar el resultado
        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(response['body'], '"No users found"')


if __name__ == '__main__':
    unittest.main()
