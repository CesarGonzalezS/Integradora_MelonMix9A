import json
import os
import unittest
from unittest.mock import patch, MagicMock
from app import lambda_handler

class TestLambdaHandler(unittest.TestCase):

    @patch("app.mysql.connector.connect")
    def test_lambda_handler_success(self, mock_connect):
        apigw_event = {
            'body': json.dumps({
                'title': 'Test Album',
                'release_date': '2023-07-08',
                'artist_id': 1
            })
        }

        # Mock de conexión y cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        response = lambda_handler(apigw_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], json.dumps('Album created successfully'))

        mock_connect.assert_called_once_with(
            host=os.environ['RDS_HOST'],
            user=os.environ['RDS_USER'],
            password=os.environ['RDS_PASSWORD'],
            database=os.environ['RDS_DB']
        )
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO albums (title, release_date, artist_id) VALUES (%s, %s, %s)",
            ('Test Album', '2023-07-08', 1)
        )
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("app.mysql.connector.connect")
    def test_lambda_handler_missing_parameters(self, mock_connect):
        apigw_event = {
            'body': json.dumps({
                'release_date': '2023-07-08',
                'artist_id': 1
            })
        }

        response = lambda_handler(apigw_event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(response['body'], json.dumps('Bad request. Missing required parameters.'))

        mock_connect.assert_not_called()

    @patch("app.mysql.connector.connect")
    def test_lambda_handler_db_error(self, mock_connect):
        apigw_event = {
            'body': json.dumps({
                'title': 'Test Album',
                'release_date': '2023-07-08',
                'artist_id': 1
            })
        }

        mock_connect.side_effect = mysql.connector.Error("Mocked DB Error")

        response = lambda_handler(apigw_event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(response['body'], json.dumps("Database error: Mocked DB Error"))

        mock_connect.assert_called_once_with(
            host=os.environ['RDS_HOST'],
            user=os.environ['RDS_USER'],
            password=os.environ['RDS_PASSWORD'],
            database=os.environ['RDS_DB']
        )

    @patch("app.mysql.connector.connect")
    def test_lambda_handler_general_error(self, mock_connect):
        apigw_event = {
            'body': json.dumps({
                'title': 'Test Album',
                'release_date': '2023-07-08',
                'artist_id': 1
            })
        }

        mock_connect.side_effect = Exception("Mocked General Error")

        response = lambda_handler(apigw_event, None)

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
