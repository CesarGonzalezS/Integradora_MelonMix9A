from cognito.login import app
import json
import unittest

mock = {
    'body': json.dumps({
        'username': 'user',
        'password': 'Peluchin1234.'
    })
}


class TestApp(unittest.TestCase):
    def test_lambda_handler(self):
        result = app.lambda_handler(mock, None)
        print(result)

