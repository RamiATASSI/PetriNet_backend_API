"""TODO"""
from PetriNet_algo.object.transition.condition import OptionalTokenMap
from PetriNet_algo.petriNet import PlaceDict
from src.PetriNet_algo.object.place import Place
from src.PetriNet_algo.object.transition.condition import ConditionSwitch, TokenMap
from src.PetriNet_algo.object.transition.operator import OperatorGraph


class Transition:
    """TODO"""
    def __init__(self,
                 transition_name: str,
                 condition_switch: ConditionSwitch,
                 operator_graph: OperatorGraph,
                 triggering_event: str = "True",
                 duration: int = 0
             ):
        # Info
        self.transition_name: str = transition_name

        # Pipeline
        self.condition_switch = condition_switch
        self.operator_graph= operator_graph
        self.consumed_tokens = []

        # Miscellaneous
        self.triggering_event: str = triggering_event
        self.duration = duration
        self.is_sensitized: bool = False
        self.is_triggered: bool = False

    def check_sensitization(self) -> bool:
        """
        TODO
        :return:
        """
        self.is_sensitized = self.condition_switch.is_condition_switch_satisfiable() is None
        return self.is_sensitized

    @DeprecationWarning
    def shortcut_trigger_if_sensitized(self):
        """
        TODO
        :return:
        """
        if self.is_sensitized:
            self.is_triggered = True
            return True
        return False

    def consume_tokens(self, places: PlaceDict) -> OptionalTokenMap:
        """
        Consume tokens that satisfy the conditions of the transition.
        :return:
            The consumed tokens.
        """
        tokens_to_consume = self.condition_switch.is_condition_switch_satisfiable()
        if tokens_to_consume is None:
            return None

        for place_id in tokens_to_consume:
            for token in tokens_to_consume[place_id]:
                places[place_id].remove(token) # TODO Remove particular token

        self.consumed_tokens = tokens_to_consume
        return tokens_to_consume

    def produce_tokens(self) -> TokenMap:
        """
        Produce the tokens of a transition.
        :return:
            The produced tokens.
        """
        # TODO Run the OperatorGraph
        pass

    def __str__(self) -> str:
        return f"{self.transition_name}(consumed_tokens={self.consumed_tokens})"
