from src.PetriNet_algo.object.place import Place


class Transition:
    def __init__(self, transition_name, transition_data: dict, places: dict[str, Place]):
        self.transition_name: str = transition_name
        self.token_consumption: dict[Place, dict] = {places[key]: value for key, value in
                                                     transition_data.get('Token_Consumption', {}).items()}
        self.triggering_event: str = transition_data.get('Triggering_Event', "True")
        self.token_production: dict[Place, dict] = {places[key]: value for key, value in
                                                    transition_data.get('Token_Production', {}).items()}
        self.is_sensitized: bool = False
        self.is_triggered: bool = False

        # NEW:
        print(f"Transitions data : {transition_data}")
        self.duration = transition_data.get('Duration', 0)  # integer seconds
        self.time_sensitized = None
        self.is_sensitized = False
        self.is_triggered = False


    def check_sensitization(self) -> bool:
        if not self.token_consumption:
            self.is_sensitized = True
            return True

        for place, token in self.token_consumption.items():
            for color, weight in token.items():
                if color not in place.tokens or place.tokens[color] < weight:
                    self.is_sensitized = False
                    return False

        self.is_sensitized = True
        return True

    def shortcut_trigger_if_sensitized(self):
        if self.is_sensitized:
            self.is_triggered = True
            return True
        return False

    def consume_tokens(self) -> dict[Place, set[str]]:
        deleted_colors = {}
        #emit('message', f"Consuming tokens for transition {self.transition_name}")
        for place, token in self.token_consumption.items():
            for color, weight in token.items():
                if weight > 0:
                    place.add_colored_tokens(color, -weight)
                    if place not in deleted_colors:
                        deleted_colors[place] = set()
                    deleted_colors[place].add(color)
        return deleted_colors

    def produce_tokens(self) -> dict[Place, set[str]]:
        added_colors = {}
        #emit('message', f"Producing tokens for transition {self.transition_name}")
        for place, token in self.token_production.items():
            for color, weight in token.items():
                if weight > 0:
                    place.add_colored_tokens(color, weight)
                    if place not in added_colors:
                        added_colors[place] = set()
                    added_colors[place].add(color)
        return added_colors

    def __str__(self) -> str:
        return self.transition_name
