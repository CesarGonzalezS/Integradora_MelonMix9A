import unittest
from unittest.mock import patch, MagicMock
import os
import json
import mysql.connector
from app import lambda_handler

class TestLambdaHandlerUpdateAlbum(unittest.TestCase):

    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password',
                             'RDS_DB': 'test_db'})
    @patch('mysql.connector.connect')
    def test_lambda_handler_success(self, mock_connect):
        # Mock de la conexión y cursor
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Mock de la ejecución de la consulta de actualización
        mock_cursor.execute.return_value = None
        mock_cursor.rowcount = 1  # Indica que se actualizó un registro

        # Ejecutar la lambda handler
        event = {
            'body': json.dumps({
                'album_id': 1,
                'title': 'Updated Album Title',
                'release_date': '2024-07-17',
                'artist_id': 1
            })
        }
        context = {}
        response = lambda_handler(event, context)

        # Verificar el resultado
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), 'Album updated successfully')

        # Verificar llamadas a funciones simuladas
        mock_connect.assert_called_once_with(
            host='test_host',
            user='test_user',
            password='test_password',
            database='test_db'
        )
        mock_cursor.execute.assert_called_once_with(
            "UPDATE albums SET title = %s, release_date = %s, artist_id = %s WHERE album_id = %s",
            ('Updated Album Title', '2024-07-17', 1, 1)
        )
        mock_cursor.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connect.return_value.close.assert_called_once()

    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password',
                             'RDS_DB': 'test_db'})
    @patch('mysql.connector.connect')
    def test_lambda_handler_album_not_found(self, mock_connect):
        # Mock de la conexión y cursor
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Mock de la ejecución de la consulta de actualización (álbum no encontrado)
        mock_cursor.execute.return_value = None
        mock_cursor.rowcount = 0  # Indica que no se actualizó ningún registro

        # Ejecutar la lambda handler
        event = {
            'body': json.dumps({
                'album_id': 999,  # ID de álbum no existente
                'title': 'Updated Album Title',
                'release_date': '2024-07-17',
                'artist_id': 1
            })
        }
        context = {}
        response = lambda_handler(event, context)

        # Verificar el resultado
        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body']), 'Album not found')

        # Verificar llamadas a funciones simuladas
        mock_connect.assert_called_once_with(
            host='test_host',
            user='test_user',
            password='test_password',
            database='test_db'
        )
        mock_cursor.execute.assert_called_once_with(
            "UPDATE albums SET title = %s, release_date = %s, artist_id = %s WHERE album_id = %s",
            ('Updated Album Title', '2024-07-17', 1, 999)
        )
        mock_cursor.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connect.return_value.close.assert_called_once()

    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password',
                             'RDS_DB': 'test_db'})
    @patch('mysql.connector.connect')
    def test_lambda_handler_missing_parameters(self, mock_connect):
        # Ejecutar la lambda handler con parámetros faltantes en el cuerpo del evento
        event = {
            'body': json.dumps({
                'title': 'Updated Album Title',
                'release_date': '2024-07-17',
                'artist_id': 1
            })
        }
        context = {}
        response = lambda_handler(event, context)

        # Verificar el resultado
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), 'Bad request. Missing required parameters.')

        # Verificar que no se realizaron llamadas a funciones simuladas
        mock_connect.assert_not_called()

    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password',
                             'RDS_DB': 'test_db'})
    @patch('mysql.connector.connect')
    def test_lambda_handler_database_error(self, mock_connect):
        # Mock de la conexión y cursor
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Simular un error de base de datos al ejecutar la consulta de actualización
        mock_cursor.execute.side_effect = mysql.connector.Error("Mock database error")

        # Ejecutar la lambda handler
        event = {
            'body': json.dumps({
                'album_id': 1,
                'title': 'Updated Album Title',
                'release_date': '2024-07-17',
                'artist_id': 1
            })
        }
        context = {}
        response = lambda_handler(event, context)

        # Verificar el resultado
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Database error', json.loads(response['body']))

        # Verificar llamadas a funciones simuladas
        mock_connect.assert_called_once_with(
            host='test_host',
            user='test_user',
            password='test_password',
            database='test_db'
        )


if __name__ == '__main__':
    unittest.main()
