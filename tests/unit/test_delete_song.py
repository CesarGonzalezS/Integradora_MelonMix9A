import json
import os
import unittest
from unittest.mock import patch, MagicMock
import mysql.connector
from mysql.connector import errorcode
from lambdas.song_management.delete_song.app import lambda_handler

class TestDeleteSongLambdaHandler(unittest.TestCase):

    @patch("mysql.connector.connect")
    def test_delete_song_success(self, mock_connect):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1

        event = {
            'pathParameters': {
                'song_id': '1'
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), 'Song deleted successfully')

        mock_connect.assert_called_once_with(
            host=os.environ['RDS_HOST'],
            user=os.environ['RDS_USER'],
            password=os.environ['RDS_PASSWORD'],
            database=os.environ['RDS_DB']
        )
        mock_cursor.execute.assert_called_once_with("DELETE FROM songs WHERE song_id = %s", ('1',))
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("mysql.connector.connect")
    def test_delete_song_not_found(self, mock_connect):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 0

        event = {
            'pathParameters': {
                'song_id': '1'
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body']), 'Song not found')

        mock_connect.assert_called_once_with(
            host=os.environ['RDS_HOST'],
            user=os.environ['RDS_USER'],
            password=os.environ['RDS_PASSWORD'],
            database=os.environ['RDS_DB']
        )
        mock_cursor.execute.assert_called_once_with("DELETE FROM songs WHERE song_id = %s", ('1',))
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("mysql.connector.connect")
    def test_delete_song_missing_parameters(self, mock_connect):
        event = {
            'pathParameters': {}
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Bad request. Missing required parameters.', json.loads(response['body']))

        mock_connect.assert_not_called()

    @patch("mysql.connector.connect")
    def test_delete_song_db_access_denied_error(self, mock_connect):
        mock_connect.side_effect = mysql.connector.Error(
            errno=errorcode.ER_ACCESS_DENIED_ERROR,
            msg="Access denied"
        )

        event = {
            'pathParameters': {
                'song_id': '1'
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Database error: Access denied', json.loads(response['body']))

    @patch("mysql.connector.connect")
    def test_delete_song_db_does_not_exist_error(self, mock_connect):
        mock_connect.side_effect = mysql.connector.Error(
            errno=errorcode.ER_BAD_DB_ERROR,
            msg="Database does not exist"
        )

        event = {
            'pathParameters': {
                'song_id': '1'
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Database error: Database does not exist', json.loads(response['body']))

    @patch("mysql.connector.connect")
    def test_delete_song_general_db_error(self, mock_connect):
        mock_connect.side_effect = mysql.connector.Error(
            errno=errorcode.CR_UNKNOWN_ERROR,
            msg="Unknown error"
        )

        event = {
            'pathParameters': {
                'song_id': '1'
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Database error: Unknown error', json.loads(response['body']))

    @patch("mysql.connector.connect")
    def test_delete_song_general_exception(self, mock_connect):
        mock_connect.side_effect = Exception("General error")

        event = {
            'pathParameters': {
                'song_id': '1'
            }
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error: General error', json.loads(response['body']))

if __name__ == '__main__':
    unittest.main()
