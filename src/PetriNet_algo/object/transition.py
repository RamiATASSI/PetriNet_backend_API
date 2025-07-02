from src.PetriNet_algo.data_structure.dict_list_builder import DictListBuilder
from src.PetriNet_algo.object.place import Place
from src.PetriNet_algo.object.token import Token
from src.PetriNet_algo.object.transition.condition import ConditionSwitch
from src.PetriNet_algo.object.transition.operator import OperatorGraph


class Transition:
    def __init__(self,
                 transition_name,
                 condition_switch: ConditionSwitch,
                 operator_graph: OperatorGraph
             ):
        # Info
        self.transition_name: str = transition_name

        # Pipeline
        self.condition_switch = condition_switch
        self.operator_graph= operator_graph
        self.consumed_tokens = list()

        # Miscellaneous
        self.triggering_event: str = ...
        self.duration = ...
        self.is_sensitized = False
        self.is_triggered = False

    def check_sensitization(self) -> bool:
        """
        TODO
        :return:
        """
        self.is_sensitized = self.condition_switch.is_condition_switch_satisfiable()
        return self.is_sensitized

    def shortcut_trigger_if_sensitized(self):
        """
        TODO
        :return:
        """
        if self.is_sensitized:
            self.is_triggered = True
            return True
        return False

    def consume_tokens(self) -> dict[Place, list[Token]]:
        """
        Consume tokens that satisfy the conditions of the transition.
        :return: The consumed tokens.
        """
        dict_list_builder = DictListBuilder[Place, Token]()
        for condition in self.conditions:
            eaten_tokens: list[Token] = condition.eat_tokens() # Get eaten Token
            dict_list_builder.append_all(condition.place, eaten_tokens) # Add to return value
            for eaten_token in eaten_tokens:
                condition.place.remove_tokens(eaten_token.token_type,)

        return dict_list_builder.build()

        # OLD
        #deleted_colors = {}
        ##emit('message', f"Consuming tokens for transition {self.transition_name}")
        #for place, token in self.token_consumption.items():
        #    for color, weight in token.items():
        #        if weight > 0:
        #            place.add_colored_tokens(color, -weight)
        #            if place not in deleted_colors:
        #                deleted_colors[place] = set()
        #            deleted_colors[place].add(color)
        #return deleted_colors

    def produce_tokens(self) -> dict[Place, set[str]]:
        """
        TODO
        :return:
        """
        # TODO
        pass

        # OLD
        #added_colors = {}
        ##emit('message', f"Producing tokens for transition {self.transition_name}")
        #for place, token in self.token_production.items():
        #    for color, weight in token.items():
        #        if weight > 0:
        #            place.add_colored_tokens(color, weight)
        #            if place not in added_colors:
        #                added_colors[place] = set()
        #            added_colors[place].add(color)
        #return added_colors

    def __str__(self) -> str:
        return f"{self.transition_name}(used_map_during_consumption={self.used_map_during_consumption}, consumed_tokens={self.consumed_tokens})"
