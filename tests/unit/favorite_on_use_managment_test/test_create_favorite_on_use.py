import os
import unittest
from unittest.mock import patch, MagicMock
import json
import mysql.connector
import lambdas.favorite_on_use_management.create_favorite_on_use.app as lambda_function

class TestLambdaHandler(unittest.TestCase):

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_successful_favorite_on_use_creation(self, mock_connect):
        # Setup mock for MySQL connection and cursor
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor()
        mock_connect.return_value = mock_connection

        event = {
            'body': json.dumps({
                'favorite_id': 1,
                'song_id': 2,
                'created_at': '2024-07-23'
            })
        }
        context = {}

        response = lambda_function.lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), 'Favorite on Use created successfully!')

        expected_query = "INSERT INTO favorite_on_use (favorite_id, song_id, created_at) VALUES (%s, %s, %s)"
        expected_values = (1, 2, '2024-07-23')
        mock_cursor.execute.assert_called_once_with(expected_query, expected_values)

if __name__ == '__main__':
    unittest.main()