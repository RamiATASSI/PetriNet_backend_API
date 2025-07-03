"""TODO"""

import copy
from typing import TypeVar, Generic

K = TypeVar('K')
V = TypeVar('V')
class DictListBuilder(Generic[K, V]):
    """
    TODO
    """
    def __init__(self):
        self.__dict__: dict[K, list[V]] = {}

    def append(self, key: K, value: V) -> None:
        """
        TODO
        :param key:
        :param value:
        :return:
        """
        if key in self.__dict__:
            self.__dict__[key].append(value)
        else:
            self.__dict__[key] = [value]

    def append_all(self, key: K, values: list[V]) -> None:
        """
        TODO
        :param key:
        :param values:
        :return: Something
        """
        if key in self.__dict__:
            for v in values:
                self.append(key, v)
        else:
            self.__dict__[key] = values

    def append_map(self, other: dict[K, list[V]]) -> None:
        """TODO"""
        for key in other:
            self.append_all(key, other[key])

    def merge_with(self, other: 'DictListBuilder') -> None:
        """TODO"""
        for key in other.__dict__:
            self.append_all(key, other.__dict__[key])

    def remove(self, key: K, value: V) -> None:
        """TODO"""
        if key in self.__dict__:
            if value in self.__dict__[key]:
                self.__dict__[key].remove(value)
                if not self.__dict__[key]:
                    self.__dict__.pop(key)
            else:
                raise ValueError(f"The Value {value} was not in the list for Key {key}")
        else:
            raise KeyError(f"The Key {key} was not in this dict {self.__dict__}")

    def remove_all(self, key, values: list[V]) -> None:
        """TODO"""
        if key in self.__dict__:
            for v in values:
                if v in self.__dict__[key]:
                    self.__dict__[key].remove(v)
                else:
                    raise ValueError(f"The Value {v} was not in the list for Key {key}")
            if not self.__dict__[key]:
                self.__dict__.pop(key)
        else:
            raise KeyError(f"The Key {key} was not in this dict {self.__dict__}")

    def remove_map(self, other: dict[K, list[V]]) -> None:
        """TODO"""
        for key in other:
            self.remove_all(key, other[key])

    def get(self, key: K) -> list[V]:
        """TODO"""
        return self.__dict__[key]

    def contains(self, key: K) -> bool:
        """TODO"""
        return key in self.__dict__

    def build(self) -> dict[K, list[V]]:
        """TODO"""
        return copy.deepcopy(self.__dict__)
