"""
TODO Module docstring
"""
import random
from typing import Callable

from PetriNet_algo.data_structure.dict_list_builder import DictListBuilder
from PetriNet_algo.object.place import Place, TokenMap
from src.PetriNet_algo.object.token import Token
from src.PetriNet_algo.object.transition.operator import OperatorId, PlaceId

type ConditionId = int

type OptionalTokenMap = None | TokenMap

####################################################################################################
############################################# Condition ############################################
####################################################################################################

class Condition:
    """
    Attributes
    ----------
    TODO Update
    condition_id : ConditionId
        The ID of the condition in the transition graph.
    place_dependencies: list[Place]
        The place into which the condition depends.
    operator_dest: list[OperatorId],
        A list of place into which the condition will randomly dispatch the token that satisfies it.
    consumption_condition: Callable[[TokenMap], OptionalTokenMap],
        A function that evaluate if the condition is true. The reason for the tuple is that some
        condition do not need tokens (or need a place to be empty). In any case, if the bool is
        false, the list[Token] is discarded.
    fetch_order: list[Token] -> list[Token]
        An ordering function that will select the token to fetch (for example, the ones who where
        there first, the Humans whose age is above 18, ...
    additional_condition: Callable[[TokenMap], bool] = lambda _: True
        (Optional) Addition conditions that would be required to run the Condition, but without
        consuming any token, for example "Place 1 must be empty", "Place 2 must be have a size of 2.
    """
    def __init__(self,
                 condition_id: ConditionId,
                 place_dependencies: list[Place],
                 operator_dest: list[OperatorId],
                 consumption_condition: Callable[[TokenMap], OptionalTokenMap],
                 fetch_order: Callable[[TokenMap], TokenMap],
                 additional_condition: Callable[[TokenMap], bool] = lambda _: True
             ):
        self.condition_id = condition_id
        self.place_dependencies = place_dependencies
        self.operator_dest = operator_dest
        self.consumption_condition = consumption_condition
        self.additional_condition = additional_condition
        self.fetch_order = fetch_order

    def fetch_tokens_copy(self) -> TokenMap:
        """
        Fetches all tokens from the place_dependencies (even ones that aren't needed for the
        condition).
        :return:
            TODO
        """
        token_map = DictListBuilder[PlaceId, Token]()
        for place in self.place_dependencies:
            token_map.append_all(place.place_name, place.get_tokens())
        return token_map.build()

    def is_condition_satisfiable(self, tokens: TokenMap) -> OptionalTokenMap:
        """
        TODO
        """
        if self.additional_condition(tokens):
            return self.consumption_condition(self.fetch_order(tokens))
        return None


####################################################################################################
########################################## Condition List ##########################################
####################################################################################################
class ConditionList:
    """TODO"""
    def __init__(self, conditions: list[Condition]):
        self.conditions = conditions

    def is_condition_list_satisfiable(self) -> OptionalTokenMap:
        """TODO"""
        # Generating (Fetching) available tokens
        tokens = DictListBuilder()
        for condition in self.conditions:
            tokens.append_map(condition.fetch_tokens_copy())
        tokens = tokens.build()

        # Checking conditions
        tokens_left = DictListBuilder()
        tokens_left.append_map(tokens)
        tokens_used = DictListBuilder()
        for condition in self.conditions:
            tokens_for_condition = condition.is_condition_satisfiable(tokens_left.build())
            if tokens_for_condition is not None:
                tokens_left.remove_map(tokens_for_condition)
                tokens_used.append_map(tokens_for_condition)
            else:
                return None
        return tokens_used.build()

    def __fetch_tokens_copy__(self) -> TokenMap:
        tokens_map = DictListBuilder()
        for condition in self.conditions:
            tokens_map.append_map(condition.fetch_tokens_copy())
        return tokens_map.build()

####################################################################################################
######################################### Condition Switch #########################################
####################################################################################################
class ConditionSwitch:
    """TODO"""
    def __init__(self, condition_lists: list[ConditionList], is_priority_ordered: bool):
        self.condition_lists = condition_lists
        self.is_priority_ordered = is_priority_ordered

    def is_condition_switch_satisfiable(self) -> OptionalTokenMap:
        """TODO"""
        if not self.is_priority_ordered:
            # We don't care that the original list is lost
            random.shuffle(self.condition_lists)

        for condition_list in self.condition_lists:
            r = condition_list.is_condition_list_satisfiable()
            if r is not None:
                return r
        return None
