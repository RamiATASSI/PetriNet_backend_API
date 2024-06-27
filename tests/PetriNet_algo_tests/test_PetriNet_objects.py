import unittest

from src.PetriNet_algo.objects import Place, Transition, jsons_to_objects, objects_to_jsons

if __name__ == '__main__':
    unittest.main()


class TestPlace(unittest.TestCase):
    def setUp(self):
        self.colors = {"Color1": object(), "Color2": object()}
        self.place_data = {
            'Color1': {'Tokens_nbr': 2, 'Action': "function11"},
            'Color2': {'Tokens_nbr': 1, 'Action': "function21"}
        }
        self.place = Place("Place1", self.place_data, self.colors)

    def test_add_colored_tokens_existing_color(self):
        self.place.add_colored_tokens("Color1", 3)
        self.assertEqual(self.place.tokens["Color1"], 5)

    def test_add_colored_tokens_new_color(self):
        self.place.add_colored_tokens("Color3", 3)
        self.assertEqual(self.place.tokens["Color3"], 3)

    def test_select_color_function_as_place_action(self):
        self.place.select_color_function_as_place_action("Color1", "new_function")
        self.assertEqual(self.place.action["Color1"], "new_function")


class TestTransition(unittest.TestCase):
    def setUp(self):
        self.places = {
            'Place1': Place("Place1", {
                'Color1': {'Tokens_nbr': 2, 'Action': "function11"},
                'Color2': {'Tokens_nbr': 1, 'Action': "function21"}
            }, {"Color1": object(), "Color2": object()}),
            'Place2': Place('Place2', {
                'Color1': {'Tokens_nbr': 0, 'Action': "function12"},
                'Color2': {'Tokens_nbr': 1, 'Action': "function22"}
            }, {"Color1": object(), "Color2": object()})
        }
        self.transition_data = {
            'Token_Consumption': {
                'Place1': {'Color1': 1, 'Color2': 1},
                'Place2': {'Color2': 1}
            },
            'Triggering_Event': 'True',
            'Token_Production': {
                'Place2': {'Color1': 2, 'Color2': 1}
            }
        }
        self.transition = Transition("Transition1", self.transition_data, self.places)

    def test_check_sensitization_sensitized(self):
        self.assertTrue(self.transition.check_sensitization())

    def test_check_sensitization_not_sensitized(self):
        self.places['Place1'].tokens['Color1'] = 0
        self.assertFalse(self.transition.check_sensitization())

    def test_is_triggered_sensitized(self):
        self.transition.check_sensitization()
        self.assertTrue(self.transition.check_triggered())

    def test_is_triggered_not_sensitized(self):
        self.transition.is_sensitized = False
        self.assertFalse(self.transition.check_triggered())

    def test_consume(self):
        consumed_places = self.transition.consume_tokens()
        self.assertEqual(self.places['Place1'].tokens['Color1'], 1)
        self.assertEqual(self.places['Place1'].tokens['Color2'], 0)
        self.assertEqual(self.places['Place2'].tokens['Color2'], 0)
        self.assertTrue('Color2' in consumed_places[self.places['Place1']])
        self.assertFalse('Color1' in consumed_places[self.places['Place2']])

    def test_produce(self):
        produced_places = self.transition.produce_tokens()
        self.assertEqual(self.places['Place2'].tokens['Color1'], 2)
        self.assertEqual(self.places['Place2'].tokens['Color2'], 2)
        self.assertTrue('Color2' in produced_places[self.places['Place2']])
        self.assertTrue('Color1' in produced_places[self.places['Place2']])
        self.assertNotIn(self.places['Place1'], produced_places)


class TestJsonExtraction(unittest.TestCase):

    def setUp(self):
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

    def test_jsons_to_objects(self):
        colors, places, transitions = jsons_to_objects(self.colors_json, self.places_json, self.transitions_json)
        self.assertEqual(len(places), 2)
        self.assertEqual(len(transitions), 2)
        self.assertEqual(places['Place1'].tokens['Color1'], 2)
        self.assertEqual(places['Place1'].tokens['Color2'], 1)
        self.assertEqual(places['Place1'].action['Color1'], "function11")
        self.assertEqual(places['Place1'].action['Color2'], "function21")
        self.assertEqual(places['Place2'].tokens['Color1'], 0)
        self.assertEqual(places['Place2'].tokens['Color2'], 0)
        self.assertEqual(places['Place2'].action['Color1'], "function12")
        self.assertEqual(places['Place2'].action['Color2'], "function22")

    def test_objects_to_jsons(self):
        colors, places, transitions = jsons_to_objects(self.colors_json, self.places_json, self.transitions_json)
        places_json, transitions_json = objects_to_jsons(places, transitions)
        self.assertEqual(places_json, self.places_json)
        self.assertEqual(transitions_json, self.transitions_json)
