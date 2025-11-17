import unittest
from app import app, storage


class SimpleFinanceTest(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        storage.clear()
        storage.update({
            '20230101': 1000,
            '20230102': -200,
            '20230201': 1500
        })

    def test_all_scenarios(self):
        response = self.client.post('/add/', data={
            'date': '20230301',
            'amount': '500'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('20230301', storage)

        response = self.client.get('/calculate/2023')
        self.assertEqual(response.status_code, 200)
        total = 1000 - 200 + 1500 + 500  # 2800
        self.assertEqual(int(response.data), total)

        response = self.client.post('/add/', data={
            'date': 'invalid_date',
            'amount': '1000'
        })
        self.assertEqual(response.status_code, 500)
        self.assertNotIn('invalid_date', storage)

        storage.clear()
        response = self.client.get('/calculate/2024')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(response.data), 0)

    def test_specific_error_cases(self):
        response = self.client.post('/add/', data={
            'date': '2023-01-01',
            'amount': '1000'
        })
        self.assertEqual(response.status_code, 500)

        response = self.client.post('/add/', data={
            'date': '20231345',
            'amount': '1000'
        })
        self.assertEqual(response.status_code, 500)

        response = self.client.post('/add/', data={
            'date': '',
            'amount': '1000'
        })
        self.assertEqual(response.status_code, 500)


if __name__ == '__main__':
    unittest.main()