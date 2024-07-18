import json
import unittest
from unittest.mock import patch, MagicMock
from pymysql import MySQLError
from lambda_function import lambda_handler

class TestLambdaHandler(unittest.TestCase):

    @patch("lambda_function.get_secret")
    @patch("lambda_function.connect_to_db")
    @patch("lambda_function.execute_query")
    @patch("lambda_function.close_connection")
    def test_lambda_handler_missing_parameters(self, mock_close_connection, mock_execute_query, mock_connect_to_db, mock_get_secret):
        # Simulate event body without album_id
        event = {
            'body': json.dumps({'invalid_key': 'value'})
        }


        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Faltan parámetros obligatorios', json.loads(response['body'])['message'])

        # Additional assertions for mock calls if needed
        mock_connect_to_db.assert_not_called()
        mock_execute_query.assert_not_called()
        mock_close_connection.assert_not_called()

    @patch("lambda_function.get_secret")
    @patch("lambda_function.connect_to_db")
    @patch("lambda_function.execute_query")
    @patch("lambda_function.close_connection")
    def test_lambda_handler_event_body_error(self, mock_close_connection, mock_execute_query, mock_connect_to_db, mock_get_secret):
        # Simulate error loading event body
        event = {
            'body': '{"invalid_json}'
        }


        response = lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error interno del servidor', json.loads(response['body'])['message'])

        mock_connect_to_db.assert_not_called()
        mock_execute_query.assert_not_called()
        mock_close_connection.assert_not_called()

if __name__ == '__main__':
    unittest.main()