import json
import unittest
from unittest.mock import patch, MagicMock
from pymysql import MySQLError
from lambdas.user_management.delete_user.app import lambda_handler


class TestLambdaHandler(unittest.TestCase):

    @patch("lambdas.user_management.delete_user.app.get_secret")
    @patch("lambdas.user_management.delete_user.app.connect_to_db")
    @patch("lambdas.user_management.delete_user.app.execute_query")
    @patch("lambdas.user_management.delete_user.app.close_connection")
    def test_lambda_handler_missing_parameters(self, mock_close_connection, mock_execute_query, mock_connect_to_db, mock_get_secret):
        event = {
            'body': json.dumps({'invalid_key': 'value'})
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Faltan parámetros obligatorios', json.loads(response['body'])['message'])

        mock_connect_to_db.assert_not_called()
        mock_execute_query.assert_not_called()
        mock_close_connection.assert_not_called()

    @patch("lambdas.user_management.delete_user.app.get_secret")
    @patch("lambdas.user_management.delete_user.app.connect_to_db")
    @patch("lambdas.user_management.delete_user.app.execute_query")
    @patch("lambdas.user_management.delete_user.app.close_connection")
    def test_lambda_handler_event_body_error(self, mock_close_connection, mock_execute_query, mock_connect_to_db, mock_get_secret):
        event = {
            'body': '{"invalid_json}'
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error interno del servidor', json.loads(response['body'])['message'])

        mock_connect_to_db.assert_not_called()
        mock_execute_query.assert_not_called()
        mock_close_connection.assert_not_called()

    @patch("lambdas.user_management.delete_user.app.get_secret")
    @patch("lambdas.user_management.delete_user.app.connect_to_db")
    @patch("lambdas.user_management.delete_user.app.execute_query")
    @patch("lambdas.user_management.delete_user.app.close_connection")
    def test_lambda_handler_success(self, mock_close_connection, mock_execute_query, mock_connect_to_db, mock_get_secret):
        event = {
            'body': json.dumps({'user_id': '123'})
        }

        mock_get_secret.return_value = {
            'host': 'localhost',
            'username': 'user',
            'password': 'password'
        }
        mock_connection = MagicMock()
        mock_connect_to_db.return_value = mock_connection
        mock_execute_query.return_value = True
        mock_connection.cursor.rowcount = 1

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Usuario eliminado exitosamente', json.loads(response['body'])['message'])

        mock_connect_to_db.assert_called_once()
        mock_execute_query.assert_called_once()
        mock_close_connection.assert_called_once()

    @patch("lambdas.user_management.delete_user.app.get_secret")
    @patch("lambdas.user_management.delete_user.app.connect_to_db")
    @patch("lambdas.user_management.delete_user.app.execute_query")
    @patch("lambdas.user_management.delete_user.app.close_connection")
    def test_lambda_handler_user_not_found(self, mock_close_connection, mock_execute_query, mock_connect_to_db, mock_get_secret):
        event = {
            'body': json.dumps({'user_id': '123'})
        }

        mock_get_secret.return_value = {
            'host': 'localhost',
            'username': 'user',
            'password': 'password'
        }
        mock_connection = MagicMock()
        mock_connect_to_db.return_value = mock_connection
        mock_execute_query.return_value = True
        mock_connection.cursor.rowcount = 0

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 404)
        self.assertIn('Usuario no encontrado', json.loads(response['body'])['message'])

        mock_connect_to_db.assert_called_once()
        mock_execute_query.assert_called_once()
        mock_close_connection.assert_called_once()


    @patch("lambdas.user_management.delete_user.app.get_secret")
    @patch("lambdas.user_management.delete_user.app.connect_to_db")
    @patch("lambdas.user_management.delete_user.app.execute_query")
    @patch("lambdas.user_management.delete_user.app.close_connection")
    def test_lambda_handler_internal_error(self, mock_close_connection, mock_execute_query, mock_connect_to_db, mock_get_secret):
        event = {
            'body': json.dumps({'user_id': '123'})
        }

        mock_get_secret.side_effect = Exception("Internal Error")

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error interno del servidor', json.loads(response['body'])['message'])

        mock_get_secret.assert_called_once()
        mock_connect_to_db.assert_not_called()
        mock_execute_query.assert_not_called()
        mock_close_connection.assert_not_called()


if __name__ == '__main__':
    unittest.main()
