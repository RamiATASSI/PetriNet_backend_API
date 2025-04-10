from src.PetriNet_algo.object.place import Place
from src.PetriNet_algo.object.transition import Transition
from .deserializer import ColorDeserializer

def jsons_to_objects(colors_json, places_json, transitions_json):
    color_deserializer = ColorDeserializer()
    colors = {}
    for color, color_data in colors_json.items():
        colors[color] = color_deserializer.compile(color_data)
    places = {}
    for place, place_data in places_json.items():
        places[place] = Place(place, place_data, colors)
    transitions = {}
    for transition, transition_data in transitions_json.items():
        transitions[transition] = Transition(transition, transition_data, places)
    return colors, places, transitions


def objects_to_jsons(places: dict[Place], transitions: dict[Transition]):
    places_json = {}
    for place_name, place in places.items():
        place_data = {}
        for color, token_count in place.tokens.items():
            place_data[color] = {
                'Tokens_nbr': token_count,
            }
        places_json[place_name] = place_data

    transitions_json = {}
    for transition_name, transition in transitions.items():
        transition_data = {
            'Is_Sensitized': transition.is_sensitized,
        }
        transitions_json[transition_name] = transition_data

    return places_json, transitions_json

def _get_state(self):
        return self.objects_to_json(self.places, self.transitions)

def main() -> None:
    transitions_json = {
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
                            },
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
                            },
                    },
                'Triggering_Event': 'True',
                'Token_Production':
                    {
                        'Place1':
                            {
                                'Color1': 1,
                                'Color2': 1
                            },
                    }
            }
    }

    places_json = {
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

    colors_json = {
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

    colors, places, transitions = jsons_to_objects(colors_json, places_json, transitions_json)
    for name, transition in transitions.items():
        print(name, "sensitization : ", transition.check_sensitization())
        print(name, "triggered : ", transition.check_triggered())


if __name__ == '__main__':
    main()
