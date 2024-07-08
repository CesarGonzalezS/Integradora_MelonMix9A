from cognito.change_password import app
import json
import unittest

mock = {
    'body': json.dumps({
        'username': 'user',
        'temporary_password': 'Peluchin123.',
        'new_password':'Peluchin1234.'
    })
}

class TestApp:
    def test_lambda_handler(self):
        result=app.lambda_handler(mock,None)
