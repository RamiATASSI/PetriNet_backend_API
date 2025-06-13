from typing import Callable

from src.PetriNet_algo.object.token import Token
from src.PetriNet_algo.object.transition.operator import OperatorId, PlaceId

type ConditionId = int

class Condition:
    """
    Attributes
    ----------
    condition_id : ConditionId
        The ID of the condition in the transition graph.
    condition : Callable[[PlaceId], (bool, list[Token])]
        A function that evaluate if the condition is true. The reason for the tuple is that some condition do not need
        tokens (or need a place to be empty). In any case, if the bool is false, the list[Token] is discarded.
    place_id_dependency : PlaceId
        The place into which the condition depends.
    operator_dest : list[OperatorId]
        A list of place into which the condition will randomly dispatch the token that satisfies it.
    """
    def __init__(self, condition_id: ConditionId, condition: Callable[[PlaceId], (bool, list[Token])],
                 place_id_dependency: PlaceId, operator_dest: list[OperatorId]):
        self.condition_id = condition_id
        self.condition = condition
        self.place_id_dependency = place_id_dependency
        # TODO Implement this here instead of the map from `Transition#condition_to_operator_map`
        self.operator_dest = operator_dest

    def is_condition_satisfiable(self) -> bool:
        """
        Look if the place on which this condition depends owns the necessary tokens to satisfy the condition.
        :return: `True` if the condition is satisfiable, `False` otherwise.
        """
        return self.condition(self.place_id_dependency)[0]

    def eating_tokens(self) -> list[Token]:
        """
        Return the token that this transition will eat. The condition need to be satisfiable. A condition in itself
        won't eat the token by itself, it is the caller responsibility to manage the tokens later.
        :return: The list of tokens that the condition will eat
        """
        (is_valid, tokens) = self.condition(self.place_id_dependency)
        assert is_valid
        return tokens
