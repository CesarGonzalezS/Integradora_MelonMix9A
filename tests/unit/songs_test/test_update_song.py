import json
import os
import unittest
from unittest.mock import patch, MagicMock
import mysql.connector
from mysql.connector import errorcode
from lambdas.song_management.update_song import lambda_handler

class TestUpdateSongLambdaHandler(unittest.TestCase):

    @patch("mysql.connector.connect")
    def test_update_song_success(self, mock_connect):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1

        event = {
            'body': json.dumps({
                'song_id': '1',
                'title': 'Updated Song',
                'duration': 300,
                'album_id': 1,
                'artist_id': 1,
                'genre': 'Rock'
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), 'Song updated successfully')

        mock_connect.assert_called_once_with(
            host=os.environ['RDS_HOST'],
            user=os.environ['RDS_USER'],
            password=os.environ['RDS_PASSWORD'],
            database=os.environ['RDS_DB']
        )
        mock_cursor.execute.assert_called_once_with(
            "UPDATE songs SET title = %s, duration = %s, album_id = %s, artist_id = %s, genre = %s WHERE song_id = %s",
            ('Updated Song', 300, 1, 1, 'Rock', '1')
        )
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("mysql.connector.connect")
    def test_update_song_not_found(self, mock_connect):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 0

        event = {
            'body': json.dumps({
                'song_id': '1',
                'title': 'Updated Song',
                'duration': 300,
                'album_id': 1,
                'artist_id': 1,
                'genre': 'Rock'
            })
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
        mock_cursor.execute.assert_called_once_with(
            "UPDATE songs SET title = %s, duration = %s, album_id = %s, artist_id = %s, genre = %s WHERE song_id = %s",
            ('Updated Song', 300, 1, 1, 'Rock', '1')
        )
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("mysql.connector.connect")
    def test_update_song_db_access_denied_error(self, mock_connect):
        mock_connect.side_effect = mysql.connector.Error(
            errno=errorcode.ER_ACCESS_DENIED_ERROR,
            msg="Access denied"
        )

        event = {
            'body': json.dumps({
                'song_id': '1',
                'title': 'Updated Song',
                'duration': 300,
                'album_id': 1,
                'artist_id': 1,
                'genre': 'Rock'
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error: Access denied', json.loads(response['body']))

    @patch("mysql.connector.connect")
    def test_update_song_db_does_not_exist_error(self, mock_connect):
        mock_connect.side_effect = mysql.connector.Error(
            errno=errorcode.ER_BAD_DB_ERROR,
            msg="Database does not exist"
        )

        event = {
            'body': json.dumps({
                'song_id': '1',
                'title': 'Updated Song',
                'duration': 300,
                'album_id': 1,
                'artist_id': 1,
                'genre': 'Rock'
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error: Database does not exist', json.loads(response['body']))

    @patch("mysql.connector.connect")
    def test_update_song_general_db_error(self, mock_connect):
        mock_connect.side_effect = mysql.connector.Error(
            errno=errorcode.CR_UNKNOWN_ERROR,
            msg="Unknown error"
        )

        event = {
            'body': json.dumps({
                'song_id': '1',
                'title': 'Updated Song',
                'duration': 300,
                'album_id': 1,
                'artist_id': 1,
                'genre': 'Rock'
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error: Unknown error', json.loads(response['body']))

    @patch("mysql.connector.connect")
    def test_update_song_general_exception(self, mock_connect):
        mock_connect.side_effect = Exception("General error")

        event = {
            'body': json.dumps({
                'song_id': '1',
                'title': 'Updated Song',
                'duration': 300,
                'album_id': 1,
                'artist_id': 1,
                'genre': 'Rock'
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error: General error', json.loads(response['body']))

if __name__ == '__main__':
    unittest.main()
