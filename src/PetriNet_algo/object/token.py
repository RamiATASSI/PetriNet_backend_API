from abc import abstractmethod
from typing import Callable

type Attribute = list[tuple[str, type]]

class Token:
    """
    An abstract class representing the tokens inside a Petri Net. Can be either a `SimpleToken` (is purely composed of
    attributes) or `SuperToken` (can be composed of other Token).

    Attributes
    ----------
    token_type : TokenType
        the type of the Token.
    attributes : dict[str, type]
        the attributes of the token, with their respective (Python) type.
    """
    def __init__(self, token_type: 'TokenType', attributes: Attribute):
        self.token_type = token_type
        self.attributes = attributes

    @abstractmethod
    def is_super_token(self) -> bool:
        """A small function to determine if a function is a SuperToken (avoid casting and instance checking)"""
        pass

    def merge(self, other: 'Token') -> 'SuperToken':
        """Default merge: only SuperToken supports merging."""
        raise TypeError(f"Cannot merge into non-super token {self!r} !")
    def split(self, selector: Callable[['SuperToken'], 'Token']) -> ('SuperToken', "Token"):
        """Default split: only SuperToken supports splitting."""
        raise TypeError(f"Cannot split non-super token {self!r} !")

class SimpleToken(Token):
    """
    A `Token` that is purely composed of attributes.

    Attributes
    ----------
    token_type : TokenType
        the type of the Token.
    attributes : dict[str, type]
        the attributes of the token, with their respective (Python) type.
    """
    def __init__(self, token_type: 'TokenType', attributes: dict[str, type]):
        super().__init__(token_type, attributes)

    def is_super_token(self) -> bool:
        return False

class SuperToken(Token):
    """
    A `Token` that can own other Tokens.

    Attributes
    ----------
    token_type : TokenType
        the type of the Token.
    attributes : dict[str, type]
        the attributes of the token, with their respective (Python) type.
    components : list[Token]
        the token that are in the `SuperToken`
    """
    def __init__(self, token_type: 'TokenType', attributes: dict[str, type], components: list[Token]):
        super().__init__(token_type, attributes)
        self.components = components

    def is_super_token(self) -> bool:
        return True
    
    def merge(self, other: Token) -> 'SuperToken':
       """
        Merge another token into this super-token. Returns the `self` SuperToken, now containing `other` as part of its components.

        Arguments:
            other: The token to merge in.
        """
       # take token in the process of merging (other) and and set its parent as the supertoken (self)
       other.parent = self
       # append token (other) to the supertoken's (self) components list: supertoken owns the token
       self.components.append(other)
       # return supertoken
       return self
    
    def split(self, selector: Callable[['SuperToken'], Token]) -> ('SuperToken', Token):
        """
        Split off one component from this super-token.
        Returns a tuple of (modified_super_token, extracted_token).  Raises a ValueError if the selector returns a token not present in components.

        Arguments:
            selector: A function that, given this super-token, returns the component to remove.
        """
        # use selector to choose which component to pull out
        comp = selector(self)
        # raise error for invalid selections
        if comp not in self.components:
            raise ValueError(f"Component {comp!r} not found in {self!r}")
        #remove chosen component from SuperToken's components list
        self.components.remove(comp)
        # set comp as root by removing parents
        comp.parent = None
        # return (self, comp)
        return self, comp

type_set: set[str] = set[str]()

class TokenType:
    """
    A node in the dynamic type forest TypeForest.

    Attributes
    ----------  
        type_name: unique identifier string
        parent:   immediate supertype or None if root (since some can be roots of their own trees)
        children: list of immediate subtypes
    """
    def __init__(self, type_name: str, parent: 'TokenType' | None = None):
        if type_name in type_set:
            raise ValueError(f"TokenType '{type_name}' already exists!")
        type_set.add(type_name)
        self.type_name: str = type_name
        self.parent: 'TokenType' | None = None
        self.children: list[TokenType] = []
        if parent is not None:
            parent.add_subtype(self)

    def add_subtype(self, subtype: 'TokenType') -> None:
        """
        Attach an existing TokenType as a child of this node. Raise ValueError if the subtype already has a parent.

        Arguments:
            subtype: The node to add as a direct child to a type tree.
        """
        if subtype.parent:
            raise ValueError(f"TokenType '{subtype.type_name}' already has a parent!")
        subtype.parent = self
        self.children.append(subtype)

    def remove_subtype(self, subtype_name: str) -> None:
        """
        Detach a child TokenType (and its subtree) from this node. Raise ValueError if no such child is found.

        Arguments: 
            subtype_name: Name of the subtype to remove from self TokenType's tree.
        """
        for i, child in enumerate(self.children):
            if child.type_name == subtype_name:
                child.parent = None
                del self.children[i]
                return
        raise ValueError(f"No subtype named '{subtype_name}' under '{self.type_name}'")
    
    def change_parent(self, new_parent: 'TokenType') -> None:
        """
        Move this node under a different parent in the forest.

        Arguments:
            new_parent: The node that will become this node's new parent.
        """
        if self.parent:
            self.parent.remove_subtype(self.type_name)
        new_parent.add_subtype(self)



class TypeForest:
    """
    Manages the dynamic qualification forest Q. This forest is empty at start, 
    must call add_type to add any number of independent roots.
    """
    
    def __init__(self):
       self._nodes: dict[str, TokenType] = {}

    def add_type(self, type_name: str, parent_name: str | None = None) -> None:
        """
        Create and register a new TokenType in the forest.

        Arguments:
            type_name: Name of the new type.
            parent_name: Name of an existing parent type, if there should be one.
        """
        parent = self._nodes.get(parent_name) if parent_name else None
        # create the new TokenType
        node = TokenType(type_name, parent)
        # ad to node dict for lookup
        self._nodes[type_name] = node
    
    def remove_type(self, type_name: str) -> None:
        """
        Remove a TokenType (and its entire subtree) from the forest. Raises ValueError if the type given is not found.

        Arguments:
            type_name: Name of the type to remove.
        """
        node = self._nodes.get(type_name)
        if not node:
            raise ValueError(f"Type '{type_name}' not found.")
        # if it's attached to a parent, unlink from that first
        if node.parent:
            node.parent.remove_subtype(type_name)
        # recursively unregister the node and all its descendants
        def unregister(n: TokenType):
            for child in list(n.children):
                unregister(child)
            # remove from dict
            del self._nodes[n.type_name]
        unregister(node)

    def change_parent(self, type_name: str, new_parent_name: str) -> None:
        """
        Move an existing type under a different parent in the forest. Raises ValueError if either of the nodes is not found.

        Arguments:
            type_name: Name of the node to move.
            new_parent_name: Name of the new parent node.
        """
        node = self._nodes.get(type_name)
        parent = self._nodes.get(new_parent_name)
        if not node or not parent:
            raise ValueError("Type or new parent not found.")
        # call to TokenType.change_parent
        node.change_parent(parent)

    def is_subtype(self, sub: str, super: str) -> bool:
        """
        Return True if node 'sub' equals or descends from node 'super'.

        Arguments:
            sub: The subtype name.
            super: The supertype name.
        """
        node = self._nodes.get(sub)
        while node is not None:
            if node.type_name == super:
                return True
            node = getattr(node, 'parent', None)
        return False
       

    def get_descendants(self, type_name: str) -> list[str]:
        """
        Return a (pre-order) list of all type_names in the subtree rooted at 'type_name'.

        Arguments:
            type_name: Root of the subtree.
        """
        # depth first search to collect all children under type_name node, pre-order traversal to top-down list children
        start = self._nodes.get(type_name)
        if start is None:
            return []

        result = []
        def dfs(node):
            result.append(node.type_name)
            for child in node.children:
                dfs(child)

        dfs(start)
        return result

    
