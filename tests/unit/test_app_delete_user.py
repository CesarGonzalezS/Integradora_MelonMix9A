import unittest
from unittest.mock import patch, MagicMock
import json
from pymysql import Error as MySQLError
from lambdas.user_management.delete_user.app import lambda_handler  # Asegúrate de que esta importación sea correcta

class TestLambdaHandler(unittest.TestCase):

    @patch('lambdas.user_management.delete_user.app.get_connection')  # Ajusta la ruta del patching según la ubicación correcta de get_connection
    def test_lambda_handler_success(self, mock_get_connection):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1

        event = {
            'body': json.dumps({
                'user_id': '1'
            })
        }
        context = {}
        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body'])['message'], 'Usuario eliminado exitosamente')

    @patch('lambdas.user_management.delete_user.app.get_connection')
    def test_lambda_handler_user_not_found(self, mock_get_connection):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 0

        event = {
            'body': json.dumps({
                'user_id': '1'
            })
        }
        context = {}
        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body'])['message'], 'Usuario no encontrado')

    def test_lambda_handler_missing_user_id(self):
        event = {
            'body': json.dumps({})
        }
        context = {}
        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], 'Faltan parámetros obligatorios')

    @patch('lambdas.user_management.delete_user.app.get_connection')
    def test_lambda_handler_db_error(self, mock_get_connection):
        mock_get_connection.side_effect = MySQLError('Database error')

        event = {
            'body': json.dumps({
                'user_id': '1'
            })
        }
        context = {}
        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertTrue('Error de base de datos' in json.loads(response['body'])['message'])

    @patch('lambdas.user_management.delete_user.app.get_connection')
    def test_lambda_handler_general_exception(self, mock_get_connection):
        mock_get_connection.side_effect = Exception('General error')

        event = {
            'body': json.dumps({
                'user_id': '1'
            })
        }
        context = {}
        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 500)
        self.assertTrue('Error interno del servidor' in json.loads(response['body'])['message'])

if __name__ == '__main__':
    unittest.main()
