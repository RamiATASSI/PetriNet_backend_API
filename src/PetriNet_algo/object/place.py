import copy

from PetriNet_algo.object.transition.condition import TokenMap
from src.PetriNet_algo.object.token import Token
from collections import deque # easier add/remove from both ends of a deque for tokens in a place


type PlaceId = str # place_name


class Place:
    def _init_(self, place_name, type_forest):
        self.place_name: str = place_name
        self.type_forest = type_forest
        # lists of mappings of root level tokens: token type -> root level token list
        self.tokens: dict[str, list[Token]] = {}
        # counts for each possible token type (roots and subtypes) to stop full lookups to Q (type_forest) each time
        self.counts: dict[str, int] = {}
        # to remove a token once a transition is sensitized, we need to know which specific one is going to get removed instead of removing it from the count like we do
        # originally, we remove the amount required from the deque's head: O(1)
        # an index of deques for all possible types for easy removal
        self.index: dict[str, deque[Token]] = {}

    '''
      Ensure the given type exists in the type forest. Raise TypeError if type not found
    '''
    def check_valid_type(self, type_name):
        # get_descendants returns an empty list for unknown types
        if not self.type_forest.get_descendants(type_name):
            raise TypeError(f"Unknown token type or qualifier: '{type_name}'")

    '''
    Helper: Increments counts and appends to a deque for every type under which this token qualifies.
    '''
    def register_token(self, token: Token):
        types = self.type_forest.get_descendants(token.token_type.type_name)
        for t in types:
            # increment count for the type t:
            self.counts[t] = self.counts.get(t, 0) + 1
            # check if a deque exists for type t
            if t not in self.index.keys():
                # if not, init the deque for type t
                self.index[t] = deque()
            # add token to the proper deque
            self.index[t].append(token) 

    '''
    Helper: Decrements counts and removes one occurrence from each type deque in index.
    '''
    def deregister_token(self, token:Token):
        types = self.type_forest.get_descendants(token.token_type.type_name)
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
        self.check_valid_type(token.token_type.type_name)
        # add to the root-level list for its type
        if token.token_type.type_name not in self.tokens:
            self.tokens[token.token_type.type_name] = []
        self.tokens[token.token_type.type_name].append(token)
        # update counts and index deques of all types affected
        self.register_token(token)

    '''
    Return total number of tokens in this Place that match the type given or any of its subtypes.
    '''
    def get_total_token_count(self, token_type: str) -> int:
        self.check_valid_type(token_type)
        return self.counts.get(token_type, 0)

    # '''
    # Remove "count" number of tokens matching the given type (or any subtype of it).
    # Returns a list of tokens removed.
    # Raises ValueError if attempted to remove more tokens than available in the Place.
    # '''
    # def remove_tokens(self, token_type: str, count:int) -> list[Token]:
    #     self.check_valid_type(token_type)
    #     available = self.counts.get(token_type, 0)
    #     if available < count:
    #         raise ValueError(
    #             f"Not enough tokens: requested {count} of '{token_type}', but only {available} available"
    #         )
    #     # init list of removed tokens
    #     removed_tokens = []
    #     # get the deque of type to remove token from
    #     deq = self.index.get(token_type)
    #     for _ in range(count):
    #         token = deq.popleft()
    #         # remove from the root-level list if present
    #         roots = self.tokens.get(token.token_type.type_name)
    #         if roots and token in roots:
    #             roots.remove(token)
    #         else:
    #             if hasattr(token, 'parent') and token.parent:
    #                 token.parent.children.remove(token)
    #         # update counts and index deques of all types affected
    #         self.deregister_token(token)
    #         removed_tokens.append(token)
    #     return removed_tokens

    """
    Remove a single instance of `token` from this place.
    Raises ValueError if the token is not found.
    """
    def remove_token(self, token: Token) -> Token:
        self.check_valid_type(token.token_type.type_name)
        available = self.counts.get(token.token_type.type_name, 0)
        if available <= 0:
            raise ValueError(
                f"No tokens of type '{token.token_type.type_name}' available in place '{self.place_name}'"
            )
        # remove from root-level list if present
        roots = self.tokens.get(token.token_type.type_name)
        if roots and token in roots:
            roots.remove(token)
        else:
            if hasattr(token, 'parent') and token.parent:
                try:
                    token.parent.children.remove(token)
                except ValueError:
                    raise ValueError(
                        f"Token {token} not found in place '{self.place_name}'"
                    )
        # update counts and index deques of all types affected
        self.deregister_token(token)
        return token


    def get_tokens(self) -> list[Token]:
        """
        Return (a copy of) all tokens in the places.
        """
        tokens = []
        for token_submap in self.tokens.keys():
            tokens.extend(self.tokens[token_submap])
        return copy.deepcopy(tokens)

    def get_token_map(self) -> TokenMap:
        """
        Returns a TokenMap object with only one entry for this place.
        :return:
        """
        return dict([(self.place_name, self.get_tokens())])

    def __str__(self) -> str:
        return self.place_name
