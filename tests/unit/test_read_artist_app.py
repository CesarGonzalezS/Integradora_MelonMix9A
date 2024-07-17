import json
import os
import unittest
from unittest.mock import patch, MagicMock
from app import lambda_handler

class TestLambdaHandler(unittest.TestCase):

    @patch("app.mysql.connector.connect")
    def test_lambda_handler_success(self, mock_connect):
        apigw_event = {
            'body': json.dumps({'artist_id': 1})
        }

        # Mock de conexión y cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = (1, 'Artist 1', 'Genre 1', 'Bio 1')

        response = lambda_handler(apigw_event, None)

        expected_body = json.dumps({
            'artist_id': 1,
            'name': 'Artist 1',
            'genre': 'Genre 1',
            'bio': 'Bio 1'
        })

        # Verificaciones
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], expected_body)

        mock_connect.assert_called_once_with(
            host=os.environ['RDS_HOST'],
            user=os.environ['RDS_USER'],
            password=os.environ['RDS_PASSWORD'],
            database=os.environ['RDS_DB']
        )
        mock_cursor.execute.assert_called_once_with("SELECT * FROM artists WHERE artist_id = %s", (1,))
        mock_cursor.fetchone.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("app.mysql.connector.connect")
    def test_lambda_handler_artist_not_found(self, mock_connect):
        apigw_event = {
            'body': json.dumps({'artist_id': 1})
        }

        # Mock de conexión y cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = None

        response = lambda_handler(apigw_event, None)

        # Verificaciones
        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(response['body'], json.dumps('Artist not found'))

        mock_connect.assert_called_once_with(
            host=os.environ['RDS_HOST'],
            user=os.environ['RDS_USER'],
            password=os.environ['RDS_PASSWORD'],
            database=os.environ['RDS_DB']
        )
        mock_cursor.execute.assert_called_once_with("SELECT * FROM artists WHERE artist_id = %s", (1,))
        mock_cursor.fetchone.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("app.mysql.connector.connect")
    def test_lambda_handler_db_error(self, mock_connect):
        apigw_event = {
            'body': json.dumps({'artist_id': 1})
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
            'body': json.dumps({'artist_id': 1})
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

    @patch("app.mysql.connector.connect")
    def test_lambda_handler_missing_parameters(self, mock_connect):
        apigw_event = {
            'body': json.dumps({})
        }

        response = lambda_handler(apigw_event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(response['body'], json.dumps('Bad request. Missing required parameters.'))

        mock_connect.assert_not_called()

if __name__ == '__main__':
    unittest.main()
