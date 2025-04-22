from enum import Enum

from src.PetriNet_algo.object.place import Place
from src.PetriNet_algo.object.token import Token, SuperToken

type PreSet  = dict[list[Place], list[Token | SuperToken]]
type PostSet = dict[list[Place], list[Token | SuperToken]]

# class syntax

class OperationType(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

class TransitionOperation:
    def __init__(self, preset: PreSet, postset: PostSet, operation_type: OperationType):
        self.preset = preset
        self.postset = postset
        self.operation_type = operation_type
    # TODO Define the operation that a Transition should be able to do

type TransitionOperations = list[TransitionOperation]

class Transition:
    def __init__(self, transition_name, transition_ops: TransitionOperations):
        self.transition_name: str = transition_name

        """The index of the TransitionOperation that was used for the trigger"""
        self.used_map_during_consumption: int = ...
        """The tokens consumed during the transition trigger"""
        self.consumed_tokens: list[Token | SuperToken] = list()


        self.triggering_event: str = ...
        self.duration = ...
        self.is_sensitized = False
        self.is_triggered = False


    def check_sensitization(self) -> bool:
        if not self.consumed_tokens:
            self.is_sensitized = True
            return True

        # TODO Update
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
        # TODO Update
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
        # TODO Update
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
        return f"{self.transition_name}(used_map_during_consumption={self.used_map_during_consumption}, consumed_tokens={self.consumed_tokens})"
