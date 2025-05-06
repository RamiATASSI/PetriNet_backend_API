token_type_names: set[str]
token_trees = set()

class Token:
    """
    Represents a single node in a static type hierarchy.

    Each Token defines one unique qualifier type in its type_name field (ex: “Mammal”, “Cat”) 
    and maintains links to its parent and any child types through its parent and children fields. 
    Once created, each type_name must be globally unique.

    Attributes:
        type_name (str):   The unique identifier for this qualifier node.
        attributes (dict): Arbitrary attributes associated with this type.
        parent (Token|None):  The immediate super-type in the hierarchy, or None if this is a root.
        children (list[Token]): All immediate sub-types of this token.
    """
    def __init__(self, type_name: str, attributes: dict[str, type], parent: "Token"):
        if type_name not in token_type_names:
            token_type_names.add(type_name)
            self.type_name = type_name
            self.parent = parent
            self.children = []
            self.attributes = attributes
        else:
            raise KeyError("The type {type_name} already exists".format(type_name=type_name))

    """
    Attach this node under a parent in the static tree.
    """
    def set_parent(self, parent: "Token"):
        self.parent = parent
    """
    Replace the children (list of sub-nodes) of this node.
    """
    def set_children(self, children: list["Token"]):
        self.children = children
    """
    Add a single child (sub-type) under this node.
    """
    def add_child(self, child: "Token"):
        self.children.append(child)
    """
    Add multiple children (sub-types) under this node at once.
    """
    def add_children(self, children: list["Token"]):
        self.children.extend(children)
    """
    Detach one existing child (sub-type) from this node.
    """
    def remove_children(self, children: list["Token"]):
        self.children.remove(children)

    """
    Check whether this node's own type_name matches the given string.
    """
    def exists(self, type_name: str) -> bool:
        return type_name in self.type_name

    def __str__(self) -> str:
        return f"Token(type={self.type_name}, attrs={self.attributes}, parent={self.parent.type_name}, children={len(self.children)})"


class SuperToken:
    """
    TODO Documentation
    """
    def __init__(self, type_name: str, attributes: dict[str, type], content: list[Token]):
        pass

    # TODO


class TypeTree:
    """
    tree[Token]
    TODO Documentation
    """

    def __init__(self, root_type: Token):
        self.root_type = root_type

    # TODO
