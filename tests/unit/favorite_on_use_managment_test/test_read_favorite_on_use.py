import unittest
from unittest.mock import patch, MagicMock
import json
import mysql.connector
import os
import lambdas.favorite_on_use_management.read_favorite_on_use.app as lambda_function  # Adjust import path as per your actual structure

class TestLambdaHandler(unittest.TestCase):

    @patch('mysql.connector.connect')
    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password', 'RDS_DB': 'test_db'})
    def test_successful_favorite_on_use_retrieval(self, mock_connect):
        # Setup mock for MySQL connection and cursor
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor()
        mock_connect.return_value = mock_connection

        # Mock the cursor to return a specific result
        mock_cursor.fetchone.return_value = {
            'favorite_on_use_id': 1,
            'song_id': 2,
            'created_at': '2024-07-23'
        }

        event = {
            'pathParameters': {
                'favorite_on_use_id': 1
            }
        }
        context = {}

        response = lambda_function.lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), {
            'favorite_on_use_id': 1,
            'song_id': 2,
            'created_at': '2024-07-23'
        })

        expected_query = "SELECT * FROM favorite_on_use WHERE favorite_on_use_id = %s"
        expected_values = (1,)
        mock_cursor.execute.assert_called_once_with(expected_query, expected_values)

if __name__ == '__main__':
    unittest.main()