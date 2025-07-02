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
            self._dict[key].extend(values)
        else:
            self._dict[key] = values

    def get(self, key: K) -> list[V]:
        return self._dict[key]

    def contains(self, key: K) -> bool:
        return key in self._dict

    def build(self):
        return self._dict.copy()