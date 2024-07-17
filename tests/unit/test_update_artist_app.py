import json
import os
import unittest
from unittest.mock import patch, MagicMock
from app import lambda_handler

class TestLambdaHandler(unittest.TestCase):

    @patch("app.mysql.connector.connect")
    def test_lambda_handler_success(self, mock_connect):
        apigw_event = {
            'body': json.dumps({'artist_id': 1, 'name': 'Updated Name', 'genre': 'Updated Genre', 'bio': 'Updated Bio'})
        }

        # Mock de conexión y cursor
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        response = lambda_handler(apigw_event, None)

        expected_body = json.dumps('Artist updated successfully')

        # Verificaciones
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], expected_body)

        mock_connect.assert_called_once_with(
            host=os.environ['RDS_HOST'],
            user=os.environ['RDS_USER'],
            password=os.environ['RDS_PASSWORD'],
            database=os.environ['RDS_DB']
        )
        mock_cursor.execute.assert_called_once_with(
            "UPDATE artists SET name = %s, genre = %s, bio = %s WHERE artist_id = %s",
            ('Updated Name', 'Updated Genre', 'Updated Bio', 1)
        )
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("app.mysql.connector.connect")
    def test_lambda_handler_no_fields_to_update(self, mock_connect):
        apigw_event = {
            'body': json.dumps({'artist_id': 1})
        }

        response = lambda_handler(apigw_event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(response['body'], json.dumps('Bad request. No fields to update.'))

        mock_connect.assert_not_called()

    @patch("app.mysql.connector.connect")
    def test_lambda_handler_db_error(self, mock_connect):
        apigw_event = {
            'body': json.dumps({'artist_id': 1, 'name': 'Updated Name'})
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
            'body': json.dumps({'artist_id': 1, 'name': 'Updated Name'})
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
