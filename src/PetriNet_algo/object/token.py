from abc import abstractmethod

type Attribute = dict[str, type]

class TokenType:
    """
    TODO
    """
    def __init__(self, type_name: str):
        assert(type_name not in type_set)
        type_set.add(type_name)
        self.type_name: str = type_name

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
    def __init__(self, token_type: TokenType, attributes: Attribute):
        self.token_type = token_type
        self.attributes = attributes
    @abstractmethod
    def is_super_token(self) -> bool:
        pass

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
    def __init__(self, token_type: TokenType, attributes: dict[str, type]):
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
    def __init__(self, token_type: TokenType, attributes: dict[str, type], components: list[Token]):
        super().__init__(token_type, attributes)
        self.components = components
    def is_super_token(self) -> bool:
        return True
    def merge(self, other: Token) -> 'SuperToken':
       # take token in the process of merging (other) and and set its parent as the supertoken (self)
       other.parent = self
       # append token (other) to the supertoken's (self) components list: supertoken owns the token
       self.components.append(other)
       # return supertoken
       return self
    def split(self, selector: callable[['SuperToken'], Token]) -> ('SuperToken', Token):
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

class TypeTree:
    """
    Manages the static qualification forest Q.
    Functions:
      - is_subtype(sub, super): whether node 'sub' is equal to or nested under another node 'super'.
      - get_descendants(type_name): list of all type_names in the static subtree whose root is type_name.
    """
    
    """
      TODO if we want to dynamically change this forest too, meaning if we want to 
      let users add new token types or change existing ones while the system is live, need to add proper methods
    """
    def __init__(self, root_type: TokenType):
        self.root_type = root_type
        self._nodes = {}
        def register(node):
            self._nodes[node.type_name] = node
            for child in node.children:
                register(child)
        register(root_type)

    
    # TODO documentation
    def is_subtype(self, sub: str, super: str) -> bool:
        node = self._nodes.get(sub)
        while node is not None:
            if node.type_name == super:
                return True
            node = getattr(node, 'parent', None)
        return False
       

    # TODO documentation
    def get_descendants(self, type_name: str) -> list[str]:
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

    
