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
        if key not in self._dict:
            new_list = self._dict.get(key)
            new_list += value
            self._dict[key] = new_list
        else:
            self._dict[key] = value

    def append_all(self, key: K, values: list[V]) -> None:
        """
        TODO
        :param key:
        :param values:
        :return: Something
        """
        if key not in self._dict:
            new_list = self._dict.get(key)
            new_list += values
            self._dict[key] = new_list
        else:
            self._dict[key] = values

    def build(self):
        return self._dict.copy()