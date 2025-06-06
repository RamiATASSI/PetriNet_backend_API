from typing import Callable

from src.PetriNet_algo.object.place import Place
from src.PetriNet_algo.object.transition.operator import OperatorId

class Condition:
    """
    TODO
    """
    def __init__(self, condition_id: int, condition: Callable,
                 places: list[Place], operator_dest: list[OperatorId]):
        self.condition_id = condition_id
        self.condition = condition
        self.places = places
        self.operator_dest = operator_dest
