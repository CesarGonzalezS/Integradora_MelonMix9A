import unittest
from unittest import mock
from lambdas.user_management.update_user.app import lambda_handler
from botocore.exceptions import ClientError
import pymysql  # Asegúrate de que pymysql esté importado

import json

class TestUpdateUserLambda(unittest.TestCase):
    @mock.patch('lambdas.user_management.update_user.app.get_secret')
    @mock.patch('lambdas.user_management.update_user.app.execute_query')
    @mock.patch('lambdas.user_management.update_user.app.connect_to_db')
    def test_lambda_handler_success(self, mock_connect_to_db, mock_execute_query, mock_get_secret):
        # Configurar los mocks
        mock_get_secret.return_value = {
            'host': 'mock_host',
            'username': 'mock_user',
            'password': 'mock_password',
            'dbname': 'mock_dbname'
        }
        mock_connect_to_db.return_value = mock.Mock()
        mock_execute_query.return_value = None

        event = {
            'user_id': '123',
            'username': 'new_username',
            'email': 'new_email@example.com',
            'password': 'new_password'
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(
            json.loads(response['body']),
            {'message': 'Usuario actualizado exitosamente'}
        )

    @mock.patch('lambdas.user_management.update_user.app.get_secret')
    @mock.patch('lambdas.user_management.update_user.app.execute_query')
    @mock.patch('lambdas.user_management.update_user.app.connect_to_db')
    def test_lambda_handler_missing_parameters(self, mock_connect_to_db, mock_execute_query, mock_get_secret):
        event = {
            'user_id': '123',
            'username': 'new_username'
            # Faltan email y password
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(
            json.loads(response['body']),
            {'message': 'Faltan parámetros requeridos'}
        )

    @mock.patch('lambdas.user_management.update_user.app.get_secret')
    def test_lambda_handler_secret_error(self, mock_get_secret):
        mock_get_secret.side_effect = ClientError(
            {'Error': {'Code': 'AccessDeniedException', 'Message': 'Access Denied'}},
            'GetSecretValue'
        )

        event = {
            'user_id': '123',
            'username': 'new_username',
            'email': 'new_email@example.com',
            'password': 'new_password'
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertTrue(
            'Error al acceder a Secrets Manager:' in json.loads(response['body'])['message']
        )

    @mock.patch('lambdas.user_management.update_user.app.get_secret')
    @mock.patch('lambdas.user_management.update_user.app.execute_query')
    @mock.patch('lambdas.user_management.update_user.app.connect_to_db')
    def test_lambda_handler_db_error(self, mock_connect_to_db, mock_execute_query, mock_get_secret):
        mock_execute_query.side_effect = pymysql.MySQLError('Database error')

        mock_get_secret.return_value = {
            'host': 'mock_host',
            'username': 'mock_user',
            'password': 'mock_password',
            'dbname': 'mock_dbname'
        }
        mock_connect_to_db.return_value = mock.Mock()

        event = {
            'user_id': '123',
            'username': 'new_username',
            'email': 'new_email@example.com',
            'password': 'new_password'
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(
            json.loads(response['body']),
            {'message': 'Error en la base de datos: Database error'}
        )

if __name__ == '__main__':
    unittest.main()
