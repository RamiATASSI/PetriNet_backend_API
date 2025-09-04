"""My Module Doc"""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic


def some_static_function(arg1: str, arg2: str) -> None:
    """
    Some static function Doc
    :param arg1: First argument
    :param arg2: Second argument
    :return: None
    """
    arg1 += arg2

class SimpleClass:
    """Simple Class Doc"""
    def __init__(self):
        """Simple Class Doc: Init"""
        pass

T = TypeVar('T')
class GenericClass(Generic[T]):
    """
    Generic Class Doc
    :type 'T': A generic type"""
    pass


class AbstractClass(ABC):
    """Abstract Class Doc"""
    def __init__(self):
        """Abstract Class Doc: Init"""
        pass

    @abstractmethod
    def abstract_method(self):
        """
        Abstract Method Doc
        :raises NotImplementedError: Abstract Method Doc
        """
        raise NotImplementedError("Abstract Method")

class HierarchicalClass(AbstractClass):
    """Hierarchical Class Doc"""
    def __init__(self):
        """Hierarchical Class Doc: Init"""
        super().__init__()

    def abstract_method(self):
        """THIS DOC SHOULD NOT APPEAR"""
        pass
