import json
import unittest
import mysql.connector
from unittest.mock import patch, MagicMock
from lambdas.user_management.read_user.app import lambda_handler, read_users
from lambdas.user_management.read_user.connection_bd import connect_to_db, execute_query, close_connection

class TestLambdaHandler(unittest.TestCase):

    @patch("lambdas.user_management.read_user.app.read_users")
    def test_lambda_handler_success(self, mock_read_users):
        mock_read_users.return_value = [
            {'user_id': 1, 'username': 'testuser', 'email': 'test@example.com', 'password': 'hashedpassword',
             'date_joined': '2022-01-01'}
        ]

        response = lambda_handler({'username': 'testuser'}, {})

        self.assertEqual(response['statusCode'], 200)
        self.assertIn('testuser', response['body'])

    @patch("lambdas.user_management.read_user.app.read_users")
    def test_lambda_handler_db_connection_error(self, mock_read_users):
        mock_read_users.side_effect = Exception("DB connection error")

        response = lambda_handler({'username': 'testuser'}, {})

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('DB connection error', response['body'])

    @patch("lambdas.user_management.read_user.app.read_users")
    def test_lambda_handler_query_error(self, mock_read_users):
        mock_read_users.side_effect = Exception("Query execution error")

        response = lambda_handler({'username': 'testuser'}, {})

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Query execution error', response['body'])

    @patch("lambdas.user_management.read_user.app.read_users")
    def test_lambda_handler_secret_manager_error(self, mock_get_secret):
        mock_get_secret.side_effect = Exception("Secrets Manager error")

        response = lambda_handler({'username': 'testuser'}, {})

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Secrets Manager error', response['body'])

    #test read_users function
    @patch("lambdas.user_management.read_user.app.connect_to_db")
    @patch("lambdas.user_management.read_user.app.execute_query")
    def test_read_users_success(self, mock_execute_query, mock_connect_to_db):
        mock_connection = MagicMock()
        mock_connect_to_db.return_value = mock_connection

        mock_execute_query.return_value = [
            {'user_id': 1, 'username': 'testuser', 'email': 'example@gmil.com', 'password': 'hashedpassword',
             'date_joined': '2022-01-01'}
        ]

        users = read_users()

        self.assertEqual(len(users), 1)
        self.assertIn('testuser', users[0].values())



    @patch("lambdas.user_management.read_user.app.connect_to_db")
    @patch("lambdas.user_management.read_user.app.execute_query")
    def test_read_users_with_username_success(self, mock_execute_query, mock_connect_to_db):
        mock_connection = MagicMock()
        mock_connect_to_db.return_value = mock_connection

        mock_execute_query.return_value = [
            {'user_id': 1, 'username': 'testuser', 'email': 'example@gmil.com', 'password': 'hashedpassword',
             'date_joined': '2022-01-01'}
        ]

        users = read_users('testuser')

        self.assertEqual(len(users), 1)
        self.assertIn('testuser', users[0].values())


    @patch("lambdas.user_management.read_user.app.connect_to_db")
    @patch("lambdas.user_management.read_user.app.execute_query")
    def test_read_users_exception(self, mock_execute_query, mock_connect_to_db):
        mock_connection = MagicMock()
        mock_connect_to_db.return_value = mock_connection

        mock_execute_query.side_effect = Exception("Query execution error")

        with self.assertRaises(Exception):
            read_users()



    @patch('lambdas.user_management.read_user.connection_bd.mysql.connector.connect')
    @patch.dict('os.environ', {
        'RDS_HOST': 'test_host',
        'RDS_USER': 'test_user',
        'RDS_PASSWORD': 'test_password',
        'RDS_DB': 'test_db'
    })
    def test_connect_to_db_success(self, mock_connect):
        # Mocking the database connection
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        connection = connect_to_db()

        mock_connect.assert_called_once_with(
            host='test_host',
            user='test_user',
            password='test_password',
            database='test_db'
        )
        self.assertEqual(connection, mock_connection)

    @patch('lambdas.user_management.read_user.connection_bd.mysql.connector.connect')
    @patch.dict('os.environ', {
        'RDS_HOST': 'test_host',
        'RDS_USER': 'test_user',
        'RDS_PASSWORD': 'test_password',
        'RDS_DB': 'test_db'
    })
    def test_connect_to_db_failure(self, mock_connect):
        # Simulate a connection failure
        mock_connect.side_effect = mysql.connector.Error("Connection error")

        with self.assertRaises(mysql.connector.Error):
            connect_to_db()

    @patch('lambdas.user_management.read_user.connection_bd.mysql.connector.connect')
    def test_execute_query_success(self, mock_connect):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        # Mocking a successful query execution
        mock_cursor.fetchall.return_value = [('result1',), ('result2',)]
        query = "SELECT * FROM test_table"

        result = execute_query(mock_connection, query)

        mock_cursor.execute.assert_called_once_with(query)
        self.assertEqual(result, [('result1',), ('result2',)])

    @patch('lambdas.user_management.read_user.connection_bd.mysql.connector.connect')
    def test_execute_query_failure(self, mock_connect):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        # Simulate a query execution failure
        mock_cursor.execute.side_effect = mysql.connector.Error("Query error")
        query = "SELECT * FROM test_table"

        with self.assertRaises(mysql.connector.Error):
            execute_query(mock_connection, query)

    @patch('lambdas.user_management.read_user.connection_bd.mysql.connector.connect')
    def test_close_connection_success(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        # Simulate a successful connection closure
        close_connection(mock_connection)

        mock_connection.close.assert_called_once()


    @patch('lambdas.user_management.read_user.connection_bd.mysql.connector.connect')
    def test_close_connection_failure(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        # Simulate a failure during connection closure
        mock_connection.close.side_effect = mysql.connector.Error("Close error")

        with self.assertRaises(mysql.connector.Error):
            close_connection(mock_connection)

if __name__ == '__main__':
    unittest.main()