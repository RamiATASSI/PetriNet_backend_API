from typing import Any
from src.PetriNet_algo.object.token import Token
from collections import deque # easier add/remove from both ends of a deque for tokens in a place


class Place:
    def _init_(self, place_name, type_tree):
        self.place_name: str = place_name
        self.type_tree = type_tree
        # lists of mappings of root level tokens: token type -> root level token list
        self.tokens: dict[str, list[Token]] = {}
        # counts for each possible token type (roots and subtypes) to stop full lookups to Q (type_tree) each time
        self.counts: dict[str, int] = {}
        # to remove a token once a transition is sensitized, we need to know which specific one is going to get removed instead of removing it from the count like we do
        # originally, we remove the amount required from the deque's head: O(1)
        # an index of deques for all possible types for easy removal
        self.index: dict[str, deque[Token]] = {}
    
    '''
      Ensure the given type exists in the type tree. Raise TypeError if type not found
    '''
    def check_valid_type(self, type_name):
        # get_descendants returns an empty list for unknown types
        if not self.type_tree.get_descendants(type_name):
            raise TypeError(f"Unknown token type or qualifier: '{type_name}'")

    '''
    Helper: Increments counts and appends to a deque for every type under which this token qualifies.
    '''
    def register_token(self, token: Token):
        types = self.type_tree.get_descendants(token.type_name)
        for t in types:
            # increment count for the type t:
            self.counts[t] = self.counts.get(t, 0) + 1
            # check if a deque exists for type t
            if t not in self.deque:
                # if not, init the deque for type t
                self.index[t] = deque()
            # add token to the proper deque
            self.index[t].append(token) 
    
    '''
    Helper: Decrements counts and removes one occurrence from each type deque in index.
    '''
    def deregister_token(self, token:Token):
        types = self.type_tree.get_descendants(token.type_name)
        for t in types:
            if self.counts[t] <= 0:
                raise ValueError(f"Token count for type '{t}' is zero for this place, cannot remove token")
            # decrement count for the type t:
            self.counts[t] = self.counts.get(t) - 1
            # remove token from the deque in index
            if t in self.index:
                try:
                    self.index[t].remove(token)
                except ValueError:
                    pass

    '''
    Insert a new Token into a Place. It is added as the root of its own tree.
    '''
    def add_token(self, token: Token):
        self.check_valid_type(token.type_name)
        # add to the root-level list for its type
        if token.type_name not in self.tokens:
            self.tokens[token.type.name] = []
        self.tokens[token.token_type].append(token)
        # update counts and index deques of all types affected
        self.register_token(token)

    '''
    Return total number of tokens in this Place that match the type given or any of its subtypes.
    '''
    def get_total_token_count(self, type:str) -> int:
        self.check_valid_type(type)
        return self.counts.get(type, 0)

    '''
    Remove "count" number of tokens matching the given type (or any subtype of it).
    Returns a list of tokens removed.
    Raises ValueError if attempted to remove more tokens than available in the Place.
    '''
    def remove_tokens(self, type:str, count:int) -> list[Token]:
        self.check_valid_type(type)
        available = self.counts.get(type, 0)
        if available < count:
            raise ValueError(
                f"Not enough tokens: requested {count} of '{type}', but only {available} available"
            )
        # init list of removed tokens
        removed_tokens = []
        # get the deque of type to remove token from
        deq = self.index.get(type)
        for _ in range(count):
            token = deq.popleft()
            # remove from the root-level list if present
            roots = self.tokens.get(token.type_name)
            if roots and token in roots:
                roots.remove(token)
            else:
                if hasattr(token, 'parent') and token.parent:
                    token.parent.children.remove(token)
            # update counts and index deques of all types affected
            self.deregister_token(token)
            removed_tokens.append(token)
        return removed_tokens
    

    def __str__(self) -> str:
        return self.place_name


## old place implementation ##
    # def __init__(self, place_name, place_data: dict, colors: dict[str, Any]):
    #     self.place_name: str = place_name
    #     self.tokens: dict[str, int] = {}
    #     self.action: dict[str, str] = {}
    #     self.colors: dict[str, Any] = colors

    #     for color, data in place_data.items():
    #         try:
    #             print(f"Initializing tokens and actions for color: {color}")
    #             self.tokens[color] = data.get('Tokens_nbr', 0)  # Default to 0 if missing
    #             self.action[color] = data.get('Action', None)  # Default to None if missing
    #         except Exception as e:
    #             raise Exception(f"Error initializing color {color}: {e}")

    # def get_colors(self) -> set[str]:
    #     return {key for key, value in self.tokens.items() if value > 0}

    # def add_colored_tokens(self, color: str, token_count: int) -> None:
    #     if color in self.tokens:
    #         self.tokens[color] += token_count
    #     else:
    #         self.tokens[color] = token_count

    # def select_color_function_as_place_action(self, color: str, function_name: str) -> None:
    #     self.action[color] = function_name

    # def launch_action(self, color: str, args=None) -> Any:
    #     if args is None:
    #         return getattr(self.colors[color], self.action[color])()
    #     else:
    #         return getattr(self.colors[color], self.action[color])(**args)

    # def describe(self) -> None:
    #     print("Place name: ", self.place_name)
    #     print("Tokens: ", self.tokens)
    #     print("Actions: ", self.action)
    #     print()

    # def __str__(self) -> str:
    #     return self.place_name
