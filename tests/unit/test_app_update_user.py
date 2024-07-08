import unittest
from unittest.mock import patch, MagicMock
from datetime import date  # Asegúrate de importar date desde datetime
import os
import json
import mysql 
from lambdas.user_management.update_user.app import lambda_handler  # Asegúrate de reemplazar con el nombre de tu módulo lambda


class TestLambdaHandler(unittest.TestCase):

    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password',
                             'RDS_DB': 'test_db'})
    @patch('mysql.connector.connect')
    def test_lambda_handler_success(self, mock_connect):
        # Mock de la conexión y cursor
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Mock de la ejecución de la consulta de actualización
        mock_cursor.execute.return_value = None
        mock_cursor.rowcount = 1  # Indica que se actualizó un registro

        # Ejecutar la lambda handler
        event = {
            'body': json.dumps({
                'user_id': 1,
                'username': 'new_username',
                'email': 'new_email@example.com',
                'password': 'new_password',
                'date_joined': '2024-07-08'
            })
        }
        context = {}
        response = lambda_handler(event, context)

        # Verificar el resultado
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), 'User updated successfully')

    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password',
                             'RDS_DB': 'test_db'})
    @patch('mysql.connector.connect')
    def test_lambda_handler_user_not_found(self, mock_connect):
        # Mock de la conexión y cursor
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Mock de la ejecución de la consulta de actualización (usuario no encontrado)
        mock_cursor.execute.return_value = None
        mock_cursor.rowcount = 0  # Indica que no se actualizó ningún registro

        # Ejecutar la lambda handler
        event = {
            'body': json.dumps({
                'user_id': 999,  # ID de usuario no existente
                'username': 'new_username',
                'email': 'new_email@example.com',
                'password': 'new_password',
                'date_joined': '2024-07-08'
            })
        }
        context = {}
        response = lambda_handler(event, context)

        # Verificar el resultado
        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body']), 'User not found')

    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password',
                             'RDS_DB': 'test_db'})
    @patch('mysql.connector.connect')
    def test_lambda_handler_missing_parameters(self, mock_connect):
        # Ejecutar la lambda handler con parámetros faltantes en el cuerpo del evento
        event = {
            'body': json.dumps({
                'user_id': 1,
                'username': 'new_username',
                'password': 'new_password',
                'date_joined': '2024-07-08'
            })
        }
        context = {}
        response = lambda_handler(event, context)

        # Verificar el resultado
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), 'Bad request. Missing required parameters.')

    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password',
                             'RDS_DB': 'test_db'})
    @patch('mysql.connector.connect')
    def test_lambda_handler_database_error(self, mock_connect):
        # Mock de la conexión y cursor
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Simular un error de base de datos al ejecutar la consulta de actualización
        mock_cursor.execute.side_effect = mysql.connector.Error("Mock database error")

        # Ejecutar la lambda handler
        event = {
            'body': json.dumps({
                'user_id': 1,
                'username': 'new_username',
                'email': 'new_email@example.com',
                'password': 'new_password',
                'date_joined': '2024-07-08'
            })
        }
        context = {}
        response = lambda_handler(event, context)

        # Verificar el resultado
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Database error', json.loads(response['body']))


if __name__ == '__main__':
    unittest.main()

