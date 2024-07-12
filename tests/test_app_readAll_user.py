import unittest
from unittest.mock import patch, MagicMock
import json
from lambdas.user_management.read_all_users.app import lambda_handler

class TestLambdaHandler(unittest.TestCase):

    @patch("lambda_function.get_secret")
    @patch("lambda_function.connect_to_db")
    @patch("lambda_function.execute_query")
    @patch("lambda_function.close_connection")
    def test_lambda_handler_success(self, mock_close_connection, mock_execute_query, mock_connect_to_db,
                                    mock_get_secret):
        # Configurar mocks
        mock_get_secret.return_value = {
            'host': 'mock-host',
            'username': 'mock-user',
            'password': 'mock-password',
            'dbname': 'mock-db'
        }
        mock_connect_to_db.return_value = MagicMock()
        mock_execute_query.return_value = [(1, 'user1', 'user1@example.com', 'password123', '2024-07-15')]

        # Crear evento para la lambda
        event = {
            'body': json.dumps({'user_id': '1'})
        }

        # Llamar a la función lambda_handler
        response = lambda_handler(event, None)

        # Aserciones
        self.assertEqual(response['statusCode'], 200)
        users = json.loads(response['body'])
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]['user_id'], 1)
        self.assertEqual(users[0]['username'], 'user1')
        self.assertEqual(users[0]['email'], 'user1@example.com')
        self.assertEqual(users[0]['password'], 'password123')
        self.assertEqual(users[0]['date_joined'], '2024-07-15')

        # Verificar llamadas a funciones mock
        mock_get_secret.assert_called_once()
        mock_connect_to_db.assert_called_once_with('mock-host', 'mock-user', 'mock-password', 'mock-db')
        mock_execute_query.assert_called_once()
        mock_close_connection.assert_called_once()

    @patch("lambda_function.get_secret")
    @patch("lambda_function.connect_to_db")
    def test_lambda_handler_database_error(self, mock_connect_to_db, mock_get_secret):
        # Configurar mocks
        mock_get_secret.return_value = {
            'host': 'mock-host',
            'username': 'mock-user',
            'password': 'mock-password',
            'dbname': 'mock-db'
        }
        mock_connect_to_db.side_effect = Exception("Database connection error")

        # Crear evento para la lambda
        event = {
            'body': json.dumps({'user_id': '1'})
        }

        # Llamar a la función lambda_handler
        response = lambda_handler(event, None)

        # Aserciones
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Database error', json.loads(response['body'])['body'])

        # Verificar llamadas a funciones mock
        mock_get_secret.assert_called_once()
        mock_connect_to_db.assert_called_once()

    @patch("lambda_function.get_secret")
    def test_lambda_handler_generic_error(self, mock_get_secret):
        # Configurar mocks
        mock_get_secret.side_effect = Exception("Secrets Manager error")

        # Crear evento para la lambda
        event = {
            'body': json.dumps({'user_id': '1'})
        }

        # Llamar a la función lambda_handler
        response = lambda_handler(event, None)

        # Aserciones
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error', json.loads(response['body'])['body'])

        # Verificar llamadas a funciones mock
        mock_get_secret.assert_called_once()

if __name__ == '__main__':
    unittest.main()

