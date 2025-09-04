"""
Data-structure that mimic a basic Map, with the twist that values are a list instead of a single
value. When merging them, the list combined instead of overwriting them.
"""

import copy
from typing import TypeVar, Generic

K = TypeVar('K')
V = TypeVar('V')
class DictListBuilder(Generic[K, V]):
    """
    Data-structure that mimic a basic dict[K, V], with the twist that values are a list instead of a
    single value. When merging them, the list combined instead of overwritten.
    :type 'K': The type of the key
    :type 'V': The type of the value in the list
    """
    def __init__(self):
        """Generate an empty DictListBuilder[K,V]."""
        self.__dict__: dict[K, list[V]] = {}

    def append(self, key: K, value: V) -> None:
        """
        Append a new value to a key. If the key does not exist, add it without error.
        :param key: The key to which the new value will be added.
        :param value: Value to add.
        :return: None
        """
        if key in self.__dict__:
            self.__dict__[key].append(value)
        else:
            self.__dict__[key] = [value]

    def append_all(self, key: K, values: list[V]) -> None:
        """
        Append new values to a key. If the key does not exist, add it without error.
        :param key: Key to which the new values will be added.
        :param values: Values to add.
        :return: None
        """
        if key in self.__dict__:
            for v in values:
                self.append(key, v)
        else:
            self.__dict__[key] = values

    def append_map(self, other: dict[K, list[V]]) -> None:
        """
        Append new values to keys. If one key does not exist, add it without error.
        :param other: The map (key -> new values) to add.
        :return: None
        """
        for key in other:
            self.append_all(key, other[key])

    def merge_with(self, other: 'DictListBuilder') -> None:
        """
        Merge this DictListBuilder with another DictListBuilder (group values by keys)
        :param other: The other DictListBuilder from which the values are fetch. Will be left
            untouched.
        :return: None
        """
        for key in other.__dict__:
            self.append_all(key, other.__dict__[key])

    def remove(self, key: K, value: V) -> None:
        """
        Remove a value from a key.
        :param key: The key from which the value will be removed.
        :param value: The value to remove.
        :raise KeyError: If the key does not exist.
        :raise ValueError: If the value does not exist for the given key.
        :return: None
        """
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
        """
        Remove values from a key.
        :param key: The key from which the values will be removed.
        :param values: The values to remove.
        :raise KeyError: If the key does not exist.
        :raise ValueError: If one of the values does not exist for the given key.
        :return: None
        """
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
        """
        Remove values from keys.
        :param other: The map (key -> values) to remove.
        :raise KeyError: If one key does not exist.
        :raise ValueError: If one of the values does not exist for the given key.
        :return: None
        """
        for key in other:
            self.remove_all(key, other[key])

    def get(self, key: K) -> list[V]:
        """
        Get the list of values for a key.
        :param key: The key of the desired values.
        :return: The list of values assigned to the key.
        """
        return self.__dict__[key]

    def contains(self, key: K) -> bool:
        """
        Check if a key is in this DictListBuilder.
        :param key: The key of the desired values.
        :return: True if the key is in this DictListBuilder. False otherwise.
        """
        return key in self.__dict__

    def build(self) -> dict[K, list[V]]:
        """
        Create an immutable snapshot of the current state of the DictListBuilder.
        :return: An immutable snapshot of the current state of the DictListBuilder.
        """
        return copy.deepcopy(self.__dict__)
