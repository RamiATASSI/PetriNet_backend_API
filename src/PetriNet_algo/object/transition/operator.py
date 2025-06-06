from abc import abstractmethod
from typing import Callable

from src.PetriNet_algo.object.place import Place
from src.PetriNet_algo.object.token import Token

"""A transformation/generator/selector function."""
type Transformation = Callable[[Token | None], Token]

"""The type for operator identification."""
type OperatorId = int
"""Void operator output."""
NO_OUTPUT_ID = -1
"""A Token and its destination."""
type Packet = (OperatorId, Token)
"""An empty packet."""
EMPTY_PACKET = (NO_OUTPUT_ID, None)

"""The type for channel identification."""
type ChannelId = int
"""The ID of the normal channel."""
NORMAL_CHANNEL_ID = 0
"""The ID of the special channel."""
SPECIAL_CHANNEL_ID = 1

########################################################################################################################
####################################################### Operator #######################################################
########################################################################################################################

class Operator:
    """
    A node inside the OperatorMatrix.

    Attributes
    ----------
    transformation: Transformation
        The transformation of the token
    operator_id: OperatorId
        The ID of this operator
    normal_output_dest: OperatorId
        The output destination of this operator for the normal channel
    special_output_dest: OperatorId
        The output destination of this operator for the special channel
    """
    def __init__(self,
                 operator_id: OperatorId,
                 normal_output_dest: OperatorId,
                 special_output_dest: OperatorId = NO_OUTPUT_ID,
                 transformation: Transformation = lambda token: token):
        self.transformation = transformation
        self.operator_id = operator_id
        self.normal_output_dest = normal_output_dest
        self.special_output_dest = special_output_dest

    @abstractmethod
    def compute(self, normal_channel_input: Token, special_channel_input: Token) -> (Packet, Packet):
        """
        TODO

        Parameters
        ----------
        normal_channel_input: Token
            The Token to use in the normal channel.
        special_channel_input: Token
            A SuperToken to use for merge and unmerge operations.

        Return
        ------
        A tuple containing the Packet for the normal channel, and a Packet for the special channel.
        """
        pass


class Move(Operator):
    def __init__(self, operator_id: OperatorId, normal_output_dest: OperatorId):
        super().__init__(operator_id, normal_output_dest)

    def compute(self, normal_channel_input: Token, special_channel_input: Token) -> (Packet, Packet):
        assert(special_channel_input is None)
        return (
            (self.normal_output_dest, normal_channel_input),
            EMPTY_PACKET
        )


class Consumer(Operator):
    def __init__(self, operator_id: OperatorId, normal_output_dest: OperatorId):
        super().__init__(operator_id, normal_output_dest)

    def compute(self, normal_channel_input: Token, special_channel_input: Token) -> (Packet, Packet):
        assert(special_channel_input is None)
        return (
            EMPTY_PACKET,
            EMPTY_PACKET
        )


class Generator(Operator):
    def __init__(self, operator_id: OperatorId, normal_output_dest: OperatorId, generator: Transformation):
        super().__init__(operator_id, normal_output_dest, transformation=generator)

    def compute(self, normal_channel_input: Token, special_channel_input: Token) -> Packet:
        assert(normal_channel_input is None)
        assert(special_channel_input is None)
        return (
            (normal_channel_input, self.transformation(None)),
            EMPTY_PACKET
        )


class Transformer(Operator):
    def __init__(self, operator_id: OperatorId, normal_output_dest: OperatorId, transformation: Transformation):
        super().__init__(operator_id, normal_output_dest, transformation=transformation)

    def compute(self, normal_channel_input: Token, special_channel_input: Token) -> (Packet, Packet):
        assert(special_channel_input is None)
        return (
            (self.normal_output_dest, self.transformation(normal_channel_input)),
            EMPTY_PACKET
        )


class Merger(Operator):
    def __init__(self, operator_id: OperatorId, normal_output_dest: OperatorId):
        super().__init__(operator_id, normal_output_dest)

    def compute(self, normal_channel_input: Token, special_channel_input: Token) -> (Packet, Packet):
        # TODO Write Merge in Token
        assert(special_channel_input.is_super_token())
        return (
            (self.normal_output_dest, special_channel_input.merge(normal_channel_input)),
            EMPTY_PACKET
        )


class Spliter(Operator):
    def __init__(self, operator_id: OperatorId, normal_output_dest: OperatorId, selector: Transformation):
        super().__init__(operator_id, normal_output_dest, transformation=selector)

    def compute(self, normal_channel_input: Token, special_channel_input: Token) -> (Packet, Packet):
        assert(normal_channel_input.is_super_token())
        # TODO Write Split in Token
        (super_token, particle) = normal_channel_input.split(self.transformation)
        return (
            (self.normal_output_dest, particle),
            (self.special_output_dest, super_token)
        )

########################################################################################################################
#################################################### Operator Graph ####################################################
########################################################################################################################

def get_batches(operators: list[Operator], inputs: list[OperatorId]) -> list[list[Operator]]:
    """
    Transform a list of operators into a list of computable batches.
    For example, with a graph
    A -> C
    B -> D & F
    C -> E
    D -> E & F
    will solve the dependencies as [[A, B], [C, D], [E, F]].

    The algorithm runs as follows:
    1. First, we generate the first batch of operators (the inputs and Generators).
    2. Then, we initialize the following variables:
        LeafConnections : Nodes that have been inserted in batches but the output is unused (we only care about the
                         output).
        PotentialNodes : The next potential nodes to be inserted in the batch. They are preceded by at least one node
                         already in the batches
        RemainingNodes : The rest of the nodes (All nodes \ { Batches u PotentialNodes })
    3. Until all operators are in some batch in the batch list, for each node in PotentialNodes, do
        Check is some LeafConnections satisfy the node. If yes
            - add in the current batch
            - remove it from the PotentialNodes
            - Add its output to the LeafConnections
            - Move its output destinations from RemainingNodes to PotentialNodes for the next batch.
        Else, it cannot be added into the current batch and go to the next PotentialNode.
    """
    def get_operator_with_id(operator_id: OperatorId) -> Operator:
        for operator in operators:
            if operator.operator_id == operator_id:
                return operator
        raise ValueError('Operator with ID {} not found'.format(operator_id))

    operator_number = len(operators)
    # Put inputs and generators inside the first batch (dependence-less)
    batches: list[list[Operator]] = [
        [operator for operator in operators if operator.operator_id in inputs or type(operator) is Generator]
    ]

    # Initialization of the algorithm
    leaf_connections: set[tuple[OperatorId, ChannelId]] = set()
    for op in batches[0]:
        if type(op) in [Move, Transformer, Merger]:
            leaf_connections.add((op.normal_output_dest, NORMAL_CHANNEL_ID))
        elif type(op) is Spliter:
            leaf_connections.add((op.normal_output_dest, NORMAL_CHANNEL_ID))
            leaf_connections.add((op.special_output_dest, SPECIAL_CHANNEL_ID))
        elif type(op) in [Consumer, Generator]:
            pass
        else:
            raise TypeError("op is not a Operator : {type} | {string}".format(type=type(op), string=str(op)))

    potential_nodes: set[Operator] = set()
    for leaf_connection in leaf_connections:
        potential_nodes.add(get_operator_with_id(leaf_connection[0]))

    remaining_nodes: set[Operator] = set(operators.copy())
    for batch in batches: # Removing operators already in batches
        for op in batch:
            remaining_nodes.remove(op)
    for op in potential_nodes: # Removing operators in potential_node
        remaining_nodes.remove(op)

    next_potential_nodes: set[Operator] = set()
    while sum([len(batch) for batch in batches]) < operator_number:
        batches.append([])

        for potential_node in potential_nodes:
            if type(potential_node) in [Move, Transformer]:
                if leaf_connections.__contains__((potential_node.operator_id, NORMAL_CHANNEL_ID)):
                    batches[-1].append(potential_node)

                    leaf_connections.add((potential_node.normal_output_dest, NORMAL_CHANNEL_ID))

                    next_node = get_operator_with_id(potential_node.normal_output_dest)
                    remaining_nodes.remove(next_node)
                    next_potential_nodes.add(next_node)
                else:
                    next_potential_nodes.add(potential_node)
            elif type(potential_node) is Consumer:
                if leaf_connections.__contains__((potential_node.operator_id, NORMAL_CHANNEL_ID)):
                    batches[-1].append(potential_node)

                    # No next node
                else:
                    next_potential_nodes.add(potential_node)
            elif type(potential_node) is Generator:
                raise RuntimeError("Generator should already in the first batch, but ")
            #elif type(potential_node) is Transformer:
            #    pass
            elif type(potential_node) is Merger:
                if leaf_connections.__contains__((potential_node.operator_id, NORMAL_CHANNEL_ID))\
                        and leaf_connections.__contains__((potential_node.operator_id, SPECIAL_CHANNEL_ID)):
                    batches[-1].append(potential_node)

                    leaf_connections.add((potential_node.normal_output_dest, NORMAL_CHANNEL_ID))

                    next_node_normal = get_operator_with_id(potential_node.normal_output_dest)
                    next_node_special = get_operator_with_id(potential_node.special_output_dest)
                    remaining_nodes.remove(next_node_normal)
                    remaining_nodes.remove(next_node_special)
                    next_potential_nodes.add(next_node_normal)
                    next_potential_nodes.add(next_node_special)
                else:
                    next_potential_nodes.add(potential_node)
                pass
            elif type(potential_node) is Spliter:
                if leaf_connections.__contains__((potential_node.operator_id, NORMAL_CHANNEL_ID)):
                    batches[-1].append(potential_node)

                    leaf_connections.add((potential_node.normal_output_dest, NORMAL_CHANNEL_ID))
                    leaf_connections.add((potential_node.special_output_dest, SPECIAL_CHANNEL_ID))

                    next_node = get_operator_with_id(potential_node.normal_output_dest)
                    remaining_nodes.remove(next_node)
                    next_potential_nodes.add(next_node)
                else:
                    next_potential_nodes.add(potential_node)
            else:
                raise TypeError("potential_node is not an operator : {} | {}".format(type(potential_node), str(potential_node)))

            potential_nodes.clear()
            potential_nodes = next_potential_nodes.copy()
            next_potential_nodes.clear()
        # END for potential_node in potential_nodes:
    # END while sum([len(batch) for batch in batches]) < operator_number:

    return batches

type PlaceId = Place
class OperatorGraph:
    """
    TODO
    """
    def __init__(self, operators: list[Operator], inputs: list[OperatorId], outputs: dict[OperatorId, PlaceId]):
        self.batches = get_batches(operators, inputs)
        self.inputs = inputs
        self.outputs = outputs
        # TODO ?

    def run(self, inputs: dict[OperatorId, Token]):
        """
        With given inputs, run them through the operators graph.

        Parameters
        ----------
        inputs: dict[OperatorId, Token]
            The input tokens.

        Returns
        -------
        dict[Place, Token]
            A map of token to put into places (the map is reversed key-value wise for convenience).
        """
        # Idea have a dynamic map of packet to dipatch in the next batch
        pass