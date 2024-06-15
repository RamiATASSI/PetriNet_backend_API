import unittest

from Flask_API.app import app


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.client1 = app.test_client()
        self.client2 = app.test_client()
        self.client1.testing = True
        self.colors_json = {
            "Color1":
                {
                    "class_name": "Humans",
                    "attributes": [
                        {"attribute_name": "attribute11", "attribute_value": "1"},
                        {"attribute_name": "attribute12", "attribute_value": "'value1'"}],
                    "functions": [
                        {"function_name": "function11", "function_core": "return self.attribute11"},
                        {"function_name": "function12", "arguments": "x, y", "function_core": "return x + y"}]
                },
            "Color2":
                {
                    "class_name": "Animals",
                    "attributes": [
                        {"attribute_name": "attribute21", "attribute_value": "2"},
                        {"attribute_name": "attribute22", "attribute_value": "'value2'"}],
                    "functions": [
                        {"function_name": "function21", "function_core": "return self.attribute21"},
                        {"function_name": "function22", "arguments": "x, y", "function_core": "return x + y"}]
                }
        }
        self.places_json = {
            'Place1':
                {
                    'Color1':
                        {
                            'Tokens_nbr': 2,
                            'Action': "function11"
                        },
                    'Color2':
                        {
                            'Tokens_nbr': 1,
                            'Action': "function21"
                        }
                },
            'Place2':
                {
                    'Color1':
                        {
                            'Tokens_nbr': 0,
                            'Action': "function12"
                        },
                    'Color2':
                        {
                            'Tokens_nbr': 0,
                            'Action': "function22"
                        }
                }
        }
        self.transitions_json = {
            'Transition1':
                {
                    'Token_Consumption':
                        {
                            'Place1':
                                {
                                    'Color1': 1,
                                    'Color2': 1
                                },
                            'Place2':
                                {
                                    'Color2': 1
                                }
                        },
                    'Triggering_Event': 'True',
                    'Token_Production':
                        {
                            'Place2':
                                {
                                    'Color1': 2,
                                    'Color2': 1
                                }
                        }
                },
            'Transition2':
                {
                    'Token_Consumption':
                        {
                            'Place1':
                                {
                                    'Color1': 1,
                                    'Color2': 1
                                }
                        },
                    'Triggering_Event': 'True',
                    'Token_Production':
                        {
                            'Place2':
                                {
                                    'Color1': 1,
                                    'Color2': 1
                                }
                        }
                }
        }


    def test_run_algorithm(self):
        response1 = self.client1.post('/Petri_run',
                                    headers={'X-User-ID': 'test-user'},
                                    json={'colors': self.colors_json, 'places': self.places_json, 'transitions': self.transitions_json})
        response2 = self.client2.post('/Petri_run',
                                    headers={'X-User-ID': 'test-user'},
                                    json={'colors': self.colors_json, 'places': self.places_json, 'transitions': self.transitions_json})
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)



if __name__ == '__main__':
    unittest.main()
