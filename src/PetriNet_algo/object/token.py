token_type_names: set[str]
token_trees = set()

class Token:
    """
    The type that a token can take
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

    # TODO Documentation of all of this
    def set_parent(self, parent: "Token"):
        self.parent = parent
    def set_children(self, children: list["Token"]):
        self.children = children
    def add_child(self, child: "Token"):
        self.children.append(child)
    def add_children(self, children: list["Token"]):
        self.children.extend(children)
    def remove_children(self, children: list["Token"]):
        self.children.remove(children)

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
