import copy
from typing import TypeVar, Generic

K = TypeVar('K')
V = TypeVar('V')
class DictListBuilder(Generic[K, V]):
    """
    TODO
    """
    def __init__(self):
        self._dict: dict[K, list[V]] = {}

    def append(self, key: K, value: V) -> None:
        """
        TODO
        :param key:
        :param value:
        :return:
        """
        if key in self._dict:
            self._dict[key].append(value)
        else:
            self._dict[key] = [value]

    def append_all(self, key: K, values: list[V]) -> None:
        """
        TODO
        :param key:
        :param values:
        :return: Something
        """
        if key in self._dict:
            for v in values:
                self.append(key, v)
        else:
            self._dict[key] = values

    def append_map(self, other: dict[K, list[V]]) -> None:
        """TODO"""
        for key in other:
            self.append_all(key, other[key])

    def merge_with(self, other: 'DictListBuilder') -> None:
        """TODO"""
        for key in other._dict:
            self.append_all(key, other._dict[key])

    def remove(self, key: K, value: V) -> None:
        """TODO"""
        if key in self._dict.keys():
            if value in self._dict[key]:
                self._dict[key].remove(value)
                if not self._dict[key]:
                    self._dict.pop(key)
            else:
                raise ValueError("The Value {} was not in the list for Key {}".format(value, key))
        else:
            raise KeyError("The Key {} was not in this dict {}".format(key, self._dict.keys()))

    def remove_all(self, key, values: list[V]) -> None:
        """TODO"""
        if key in self._dict.keys():
            for v in values:
                if v in self._dict[key]:
                    self._dict[key].remove(v)
                else:
                    raise ValueError("The Value {} was not in the list for Key {}".format(v, key))
            if not self._dict[key]:
                self._dict.pop(key)
        else:
            raise KeyError("The Key {} was not in this dict {}".format(key, self._dict.keys()))

    def remove_map(self, other: dict[K, list[V]]) -> None:
        for key in other:
            self.remove_all(key, other[key])

    def get(self, key: K) -> list[V]:
        """TODO"""
        return self._dict[key]

    def contains(self, key: K) -> bool:
        return key in self._dict

    def build(self) -> dict[K, list[V]]:
        return copy.deepcopy(self._dict)