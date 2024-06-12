import unittest

from Flask_API.app import app


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_run_algorithm(self):
        response = self.client.post('/api/run_algorithm', json={})
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data['message'], 'Algorithm started successfully')

    def test_get_variable1(self):
        self.client.post('/api/run_algorithm', json={})
        response = self.client.get('/api/get_variable1')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn('variable1', json_data)


if __name__ == '__main__':
    unittest.main()
