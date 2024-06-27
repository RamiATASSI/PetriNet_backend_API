from typing import Any

from .deserializer import ColorDeserializer


class Place:
    def __init__(self, place_name, place_data: dict, colors: dict[str, Any]):
        self.place_name: str = place_name
        self.tokens: dict[str, int] = {}
        self.action: dict[str, str] = {}
        self.colors: dict[str, Any] = colors
        for color, data in place_data.items():
            self.tokens[color] = data['Tokens_nbr']
            self.action[color] = data['Action']

    def get_colors(self) -> set[str]:
        return {key for key, value in self.tokens.items() if value > 0}

    def add_colored_tokens(self, color: str, token_count: int) -> None:
        if color in self.tokens:
            self.tokens[color] += token_count
        else:
            self.tokens[color] = token_count

    def select_color_function_as_place_action(self, color: str, function_name: str) -> None:
        self.action[color] = function_name

    def launch_action(self, color: str, args=None) -> Any:
        if args is None:
            return getattr(self.colors[color], self.action[color])()
        else:
            return getattr(self.colors[color], self.action[color])(**args)

    def describe(self) -> None:
        print("Place name: ", self.place_name)
        print("Tokens: ", self.tokens)
        print("Actions: ", self.action)
        print()

    def __str__(self) -> str:
        return self.place_name


class Transition:
    def __init__(self, transition_name, transition_data: dict, places: dict[str, Place]):
        self.transition_name: str = transition_name
        self.token_consumption: dict[Place, dict] = {places[key]: value for key, value in
                                                     transition_data.get('Token_Consumption', {}).items()}
        self.triggering_event: str = transition_data.get('Triggering_Event', "None")
        self.token_production: dict[Place, dict] = {places[key]: value for key, value in
                                                    transition_data.get('Token_Production', {}).items()}
        self.is_sensitized: bool = False

    def check_sensitization(self) -> bool:
        if not self.token_consumption:
            return False
        for place, token in self.token_consumption.items():
            for color, weight in token.items():
                if place.tokens[color] < weight:
                    self.is_sensitized = False
                    return False
        self.is_sensitized = True
        return True

    def check_triggered(self) -> bool:
        if self.is_sensitized:
            if eval(self.triggering_event):
                self.is_sensitized = False
                return True
        return False

    def consume_tokens(self) -> dict[Place, set[str]]:
        deleted_colors = {}
        for place, token in self.token_consumption.items():
            for color, weight in token.items():
                place.add_colored_tokens(color, -weight)
                if place not in deleted_colors:
                    deleted_colors[place] = set()
                deleted_colors[place].add(color)
        return deleted_colors

    def produce_tokens(self) -> dict[Place, set[str]]:
        added_colors = {}
        for place, token in self.token_production.items():
            for color, weight in token.items():
                place.add_colored_tokens(color, weight)
                if place not in added_colors:
                    added_colors[place] = set()
                added_colors[place].add(color)
        return added_colors

    def describe(self) -> None:
        print("Transition name: ", self.transition_name)
        print("Token consumption: ",
              ', '.join(f"{str(place)} : {str(token)}" for place, token in self.token_consumption.items()))
        print("Triggering event: ", self.triggering_event)
        print("Token production: ",
              ', '.join(f"{str(place)} : {str(token)}" for place, token in self.token_production.items()))
        print("Sensitization: ", self.is_sensitized)
        print()

    def __str__(self) -> str:
        return self.transition_name


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
                'Action': place.action[color]
            }
        places_json[place_name] = place_data

    transitions_json = {}
    for transition_name, transition in transitions.items():
        transition_data = {
            'Token_Consumption': {str(place): value for place, value in transition.token_consumption.items()},
            'Triggering_Event': transition.triggering_event,
            'Token_Production': {str(place): value for place, value in transition.token_production.items()},
        }
        transitions_json[transition_name] = transition_data

    return places_json, transitions_json

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
