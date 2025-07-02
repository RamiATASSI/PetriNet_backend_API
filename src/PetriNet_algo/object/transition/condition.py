from typing import Callable

from src.PetriNet_algo.object.token import Token
from src.PetriNet_algo.object.transition.operator import OperatorId, PlaceId

type ConditionId = int

########################################################################################################################
####################################################### Condition ######################################################
########################################################################################################################

class Condition:
    """
    Attributes
    ----------
    condition_id : ConditionId
        The ID of the condition in the transition graph.
    condition : Callable[[PlaceId], (bool, list[Token])]
        A function that evaluate if the condition is true. The reason for the tuple is that some condition do not need
        tokens (or need a place to be empty). In any case, if the bool is false, the list[Token] is discarded.
    place_dependencies : PlaceId
        The place into which the condition depends.
    fetch_order: list[Token] -> list[Token]
        An ordering function that will select the token to fetch (for example, the ones who where there first, the
        Humans whose age is above 18, ...
    operator_dest : list[OperatorId]
        A list of place into which the condition will randomly dispatch the token that satisfies it.
    """
    def __init__(self,
                 condition_id: ConditionId,
                 place_dependencies: list[PlaceId],
                 operator_dest: list[OperatorId],
                 consumption_condition: Callable[[dict[PlaceId, list[Token]]], (bool, list[Token])],
                 fetch_order: Callable[[list[Token]], list[Token]],
                 additional_condition: Callable[[dict[PlaceId, list[Token]]], bool] = lambda _: True
             ):
        self.condition_id = condition_id
        self.place_dependencies = place_dependencies
        self.operator_dest = operator_dest
        self.consumption_condition = consumption_condition
        self.additional_condition = additional_condition
        self.fetch_order = fetch_order

    def fetch_tokens_copy(self) -> dict[PlaceId, list[Token]]:
        # TODO
        ...

    def is_condition_satisfiable(self) -> bool:
        """
        Look if the place on which this condition depends owns the necessary tokens to satisfy the condition.
        :return: `True` if the condition is satisfiable, `False` otherwise.
        """
        # TODO Update
        return self.condition(self.place_id_dependency)[0]


########################################################################################################################
#################################################### Condition List ####################################################
########################################################################################################################
class ConditionList:
    def __init__(self, conditions: list[Condition]):
        self.conditions = conditions

    def is_condition_list_satisfiable(self, tokens: dict[PlaceId, list[Token]]) -> bool:
        # TODO
        ...

    def fetch_tokens_copy(self) -> dict[PlaceId, list[Token]]:
        # TODO
        ...

########################################################################################################################
################################################### Condition Switch ###################################################
########################################################################################################################
class ConditionSwitch:
    def __init__(self, condition_list: list[ConditionList], is_priority_ordered: bool):
        self.condition_list = condition_list
        self.is_priority_ordered = is_priority_ordered

    #  is_satisfiable()
    def is_condition_switch_satisfiable(self):
        # TODO
        ...

    def __fetch_tokens_copy__(self):
        # TODO
        ...
