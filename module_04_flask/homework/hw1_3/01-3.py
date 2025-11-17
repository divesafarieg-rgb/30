import unittest
import json
from your_app import app


class TestRegistrationValidators(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_valid_email(self):
        data = {
            'email': 'test@example.com',
            'password': 'Password123',
            'username': 'testuser'
        }
        response = self.app.post('/registration', json=data)
        self.assertEqual(response.status_code, 200)

    def test_invalid_email(self):
        data = {
            'email': 'invalid-email',
            'password': 'Password123',
            'username': 'testuser'
        }
        response = self.app.post('/registration', json=data)
        self.assertEqual(response.status_code, 400)

    def test_valid_password(self):
        data = {
            'email': 'test@example.com',
            'password': 'StrongPass123',
            'username': 'testuser'
        }
        response = self.app.post('/registration', json=data)
        self.assertEqual(response.status_code, 200)

    def test_invalid_password_short(self):
        data = {
            'email': 'test@example.com',
            'password': '123',
            'username': 'testuser'
        }
        response = self.app.post('/registration', json=data)
        self.assertEqual(response.status_code, 400)

    def test_valid_username(self):
        data = {
            'email': 'test@example.com',
            'password': 'Password123',
            'username': 'valid_user123'
        }
        response = self.app.post('/registration', json=data)
        self.assertEqual(response.status_code, 200)

    def test_invalid_username_special_chars(self):
        data = {
            'email': 'test@example.com',
            'password': 'Password123',
            'username': 'user@name!'
        }
        response = self.app.post('/registration', json=data)
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
