import json
import os
import unittest
from unittest.mock import patch, MagicMock
from mysql.connector import Error as MySQLError
from delete_album import lambda_handler

class TestLambdaHandler(unittest.TestCase):

    @patch("delete_album.mysql.connector.connect")
    def test_lambda_handler_success(self, mock_connect):
        event = {
            'pathParameters': {'album_id': '1'}
        }

        # Mock connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        response = lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], json.dumps('Album deleted successfully'))

        mock_connect.assert_called_once_with(
            host=os.environ['RDS_HOST'],
            user=os.environ['RDS_USER'],
            password=os.environ['RDS_PASSWORD'],
            database=os.environ['RDS_DB']
        )
        mock_cursor.execute.assert_called_once_with(
            "DELETE FROM albums WHERE album_id = %s",
            ('1',)
        )
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("delete_album.mysql.connector.connect")
    def test_lambda_handler_album_not_found(self, mock_connect):
        event = {
            'pathParameters': {'album_id': '999'}
        }

        # Mock connection and cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 0
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        response = lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(response['body'], json.dumps('Album not found'))

        mock_connect.assert_called_once_with(
            host=os.environ['RDS_HOST'],
            user=os.environ['RDS_USER'],
            password=os.environ['RDS_PASSWORD'],
            database=os.environ['RDS_DB']
        )
        mock_cursor.execute.assert_called_once_with(
            "DELETE FROM albums WHERE album_id = %s",
            ('999',)
        )
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("delete_album.mysql.connector.connect")
    def test_lambda_handler_db_error(self, mock_connect):
        event = {
            'pathParameters': {'album_id': '1'}
        }

        mock_connect.side_effect = MySQLError("Mocked DB Error")

        response = lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(response['body'], json.dumps("Database error: Mocked DB Error"))

        mock_connect.assert_called_once_with(
            host=os.environ['RDS_HOST'],
            user=os.environ['RDS_USER'],
            password=os.environ['RDS_PASSWORD'],
            database=os.environ['RDS_DB']
        )

    @patch("delete_album.mysql.connector.connect")
    def test_lambda_handler_general_error(self, mock_connect):
        event = {
            'pathParameters': {'album_id': '1'}
        }

        mock_connect.side_effect = Exception("Mocked General Error")

        response = lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(response['body'], json.dumps("Error: Mocked General Error"))

        mock_connect.assert_called_once_with(
            host=os.environ['RDS_HOST'],
            user=os.environ['RDS_USER'],
            password=os.environ['RDS_PASSWORD'],
            database=os.environ['RDS_DB']
        )

if __name__ == '__main__':
    unittest.main()
