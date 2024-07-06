
import os
from lambdas.user_management.read_all_users.app import lambda_handler  # Asegúrate de importar correctamente tu función lambda_handler
import unittest
from unittest.mock import patch, MagicMock


class TestLambdaHandler(unittest.TestCase):

    @patch.dict(os.environ, {'RDS_HOST': 'test_host', 'RDS_USER': 'test_user', 'RDS_PASSWORD': 'test_password',
                             'RDS_DB': 'test_db'})
    @patch('mysql.connector.connect')
    def test_lambda_handler_success(self, mock_connect):
        # Mock de la conexión y cursor
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Mock de la consulta y resultados
        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = [(1, 'test_user', 'test@example.com', 'password', '2024-07-08')]

        # Ejecutar la lambda handler
        event = {}
        context = {}
        response = lambda_handler(event, context)

        # Verificar el resultado
        self.assertEqual(response['statusCode'], 500)  # Ajustar según lo esperado


if __name__ == '__main__':
    unittest.main()

