"""
TODO

TODO This part might contains some 'defensive-programing' and some 'non-defensive-programing'.

TODO Instead of Token having a `dict[str, (type, Any)]` (`{name: (type, value)}`), it would be
 nice to have the attribute list defined in the TokenType, and the Token holding a
 `dict[(str, type), Any]` (`{(name, type) : Value}`).

TODO Some type hint could be better, such as precising Simple/Super-Token.
"""

from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import Callable
from src.PetriNet_algo.data_structure.dict_list_builder import DictListBuilder
from src.PetriNet_algo.object.place import PlaceId
from src.PetriNet_algo.object.token import Token, AttributeK, SuperToken

"""A transformation/generator/selector function."""
type Transformation = Callable[[Token | None], Token]

"""The type for channel identification."""
type ChannelId = int
"""The ID of a void channel. Should not be used for non-Output operators"""
VOID_CHANNEL_ID = -1
"""The ID of the normal channel."""
NORMAL_CHANNEL_ID = 0
"""The ID of the special channel."""
SPECIAL_CHANNEL_ID = 1

"""The type for operator identification."""
type OperatorId = int
"""Void operator output."""
VOID_OUTPUT_ID = -1

"""A Token and its destination."""
type Packet = tuple[OperatorId, ChannelId, Token]
"""An empty packet."""
EMPTY_PACKET = (VOID_OUTPUT_ID, VOID_CHANNEL_ID, None)

####################################################################################################
############################################# Operator #############################################
####################################################################################################
class Operator(ABC):
    """
    A node inside the OperatorGraph.

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
                 special_output_dest: OperatorId = VOID_OUTPUT_ID,
                 transformation: Transformation = lambda token: token):
        self.operator_id = operator_id
        self.transformation = transformation

        self.normal_output_dest = normal_output_dest
        self.normal_input_channel: None | Token = None
        self.special_output_dest = special_output_dest
        self.special_input_channel: None | Token = None

    def ingest_packet(self, packet: Packet):
        """TODO"""
        assert packet[0] == self.operator_id
        if packet[1] == NORMAL_CHANNEL_ID:
            if self.normal_input_channel is None:
                self.normal_input_channel = packet[2]
            else:
                raise RuntimeError(f"Normal channel of operator {self.operator_id} "
                                   f"is already occupied")
        elif packet[1] == SPECIAL_CHANNEL_ID:
            if self.special_input_channel is None:
                self.special_input_channel = packet[2]
            else:
                raise RuntimeError(f"Special channel of operator {self.operator_id} "
                                   f"is already occupied")
        else:
            raise RuntimeError(f"Channel ID of packet {packet} is not valid")

    def __clear__(self):
        self.normal_input_channel = None
        self.special_input_channel = None

    @abstractmethod
    def __compute__(self) -> list[Packet]:
        """
        TODO

        :return: A tuple containing the Packet for the normal channel, and a Packet for the special channel.
        """

    @abstractmethod
    def __is_computable__(self) -> bool:
        """TODO"""

    def compute(self) -> list[Packet]:
        """
        TODO
        """
        if self.__is_computable__():
            produced_tokens = self.__compute__()
            self.__clear__()
            return produced_tokens
        # DEBUG: "Operator {} is not computable".format(self.operator_id)
        return []


class Move(Operator):
    """TODO"""
    def __init__(self, operator_id: OperatorId, normal_output_dest: OperatorId):
        super().__init__(operator_id, normal_output_dest)

    def __compute__(self) -> list[Packet]:
        assert self.special_input_channel is None
        return [(self.normal_output_dest, NORMAL_CHANNEL_ID, self.normal_input_channel)]

    def __is_computable__(self) -> bool:
        return self.normal_input_channel is not None and self.special_input_channel is None


class Transformer(Operator):
    """TODO"""
    def __init__(self,
                 operator_id: OperatorId,
                 normal_output_dest: OperatorId,
                 transformation: Transformation
             ):
        super().__init__(operator_id, normal_output_dest, transformation=transformation)

    def __compute__(self) -> list[Packet]:
        assert self.special_input_channel is None
        transformed_tokens = self.transformation(self.normal_input_channel)
        return [(self.normal_output_dest, NORMAL_CHANNEL_ID, transformed_tokens)]

    def __is_computable__(self) -> bool:
        return self.normal_input_channel is not None and self.special_input_channel is None


class Duplicate(Operator):
    """TODO"""
    def __init__(self, operator_id: OperatorId, normal_output_dest: OperatorId, special_output_dest: OperatorId):
        super().__init__(operator_id, normal_output_dest, special_output_dest)

    def __compute__(self) -> list[Packet]:
        return [
            (self.normal_output_dest,  NORMAL_CHANNEL_ID,  self.normal_input_channel),
            (self.special_output_dest, SPECIAL_CHANNEL_ID, self.normal_input_channel.copy()),
        ]

    def __is_computable__(self) -> bool:
        return self.normal_input_channel is not None and self.special_input_channel is None


class Import(Operator):
    """TODO"""
    def __init__(self,
                 operator_id: OperatorId,
                 special_output_dest: OperatorId,
                 attribute_key_in: AttributeK,
                 attribute_key_out: AttributeK
             ):
        super().__init__(operator_id, special_output_dest)
        self.attribute_key_in = attribute_key_in
        self.attribute_key_out = attribute_key_out

    def __compute__(self) -> list[Packet]:
        token = self.normal_input_channel
        token_to_import_from = self.special_input_channel
        attribute_val = token_to_import_from.attributes[self.attribute_key_in]
        token.attributes[self.attribute_key_out] = attribute_val

        return [
            (self.normal_output_dest, NORMAL_CHANNEL_ID, token),
        ]

    def __is_computable__(self) -> bool:
        return self.normal_input_channel is not None and self.special_input_channel is not None


class Generator(Operator):
    """TODO"""
    def __init__(self,
                 operator_id: OperatorId,
                 normal_output_dest: OperatorId,
                 generator: Transformation
             ):
        super().__init__(operator_id, normal_output_dest, transformation=generator)

    def __compute__(self) -> list[Packet]:
        assert self.normal_input_channel is None
        assert self.special_input_channel is None
        return [(self.normal_output_dest, NORMAL_CHANNEL_ID, self.transformation(None))]

    def __is_computable__(self) -> bool:
        return self.normal_input_channel is None and self.special_input_channel is None


class Consumer(Operator):
    """TODO"""
    def __init__(self, operator_id: OperatorId):
        super().__init__(operator_id, VOID_CHANNEL_ID)

    def __compute__(self) -> list[Packet]:
        assert self.special_input_channel is None
        return []

    def __is_computable__(self) -> bool:
        return self.normal_input_channel is not None and self.special_input_channel is None


class Merger(Operator):
    """TODO"""
    def __init__(self,
                 operator_id: OperatorId,
                 normal_output_dest: OperatorId,
                 ordering: Callable[[Token], None]
             ):
        super().__init__(operator_id, normal_output_dest)
        self.ordering: Callable[[Token], None] = ordering

    def __compute__(self) -> list[Packet]:
        assert self.special_input_channel.is_super_token()
        self.special_input_channel.merge(self.normal_input_channel)
        self.ordering(self.special_input_channel)

        return [(self.normal_output_dest, NORMAL_CHANNEL_ID, self.special_input_channel)]

    def __is_computable__(self) -> bool:
        return self.normal_input_channel is not None and self.special_input_channel is not None


class Splitter(Operator):
    """TODO"""
    def __init__(self,
                 operator_id: OperatorId,
                 normal_output_dest: OperatorId,
                 special_output_dest: OperatorId,
                 selector: Transformation
             ):
        super().__init__(operator_id, normal_output_dest, special_output_dest, transformation=selector)

    def __compute__(self) -> list[Packet]:
        assert self.normal_input_channel.is_super_token()
        # TODO Write Split in Token
        (super_token, particle) = self.normal_input_channel.split(self.transformation)
        return [
            (self.normal_output_dest, NORMAL_CHANNEL_ID, particle),
            (self.special_output_dest, SPECIAL_CHANNEL_ID, super_token)
        ]

    def __is_computable__(self) -> bool:
        return self.normal_input_channel is not None and self.special_input_channel is None


class Output(Operator):
    """TODO"""
    def __init__(self,
                 operator_id: OperatorId,
                 dest_place: PlaceId
             ):
        super().__init__(operator_id, VOID_CHANNEL_ID)
        self.dest_place = dest_place

    def __compute__(self) -> list[Packet]:
        raise RuntimeError(f"An Output Operator {self.operator_id} is not computable")

    def __is_computable__(self) -> bool:
        return False

    def retrieve(self) -> dict[PlaceId, Token]:
        """
        TODO
        """
        tokens_to_output = dict([(self.dest_place, self.normal_input_channel)])
        self.__clear__()
        return tokens_to_output


####################################################################################################
########################################## Operator Graph ##########################################
####################################################################################################

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
        - LeafConnections : Nodes that have been inserted in batches but the output is unused (we
            only care about the output).
        - PotentialNodes : The next potential nodes to be inserted in the batch. They are preceded
            by at least one node already in the batches
        - RemainingNodes : The rest of the nodes (All nodes -- { Batches u PotentialNodes })
    3. Until all operators are in some batch in the batch list, for each node in PotentialNodes, do
        - Check is some LeafConnections satisfy the node. If yes
            - add in the current batch
            - remove it from the PotentialNodes
            - Add its output to the LeafConnections
            - Move its output destinations from RemainingNodes to PotentialNodes for the next batch.
        - Else, it cannot be added into the current batch and go to the next PotentialNode.
    """
    if not operators:
        return []
    def get_operator_with_id(operator_id: OperatorId) -> Operator:
        """
        TODO
        """
        for operator in operators:
            if operator.operator_id == operator_id:
                return operator
        raise ValueError(f"Operator with ID {operator_id} not found")

    batch0 = [op for op in operators if type(op) is Generator]
    batch1 = [op for op in operators if op.operator_id in inputs and type(op) is not Output]
    batch9 = [op for op in operators if type(op) is Output]
    leftover_op = [op for op in operators if op not in batch0 + batch1 + batch9]

    if not batch0 and not batch1:
        # There are no input and no generator -> the graph should only pure outputs
        assert not leftover_op
        return [batch9]

    # Getting all connections
    batch0_connection: list[tuple[int, int]] = []
    batch1_connection: list[tuple[int, int]] = []
    connections: list[tuple[int, int]] = []
    for op in operators:
        t = type(op)
        if t in [Consumer, Output]:
            pass
        elif t in [Generator]:
            batch0_connection.append((op.operator_id, op.normal_output_dest))
        elif t in [Move, Transformer, Import, Merger]:
            if op.operator_id in inputs:
                batch1_connection.append((op.operator_id, op.normal_output_dest))
            else:
                connections.append((op.operator_id, op.normal_output_dest))
            pass
        elif t in [Duplicate, Splitter]:
            if op.operator_id in inputs:
                batch1_connection.append( (op.operator_id, op.normal_output_dest) )
                batch1_connection.append((op.operator_id, op.special_output_dest))
            else:
                connections.append( (op.operator_id, op.normal_output_dest) )
                connections.append((op.operator_id, op.special_output_dest))
        else:
            raise TypeError(f"Operator {op.operator_id} is not an operator")

    # Initialization from batch0 and 1 : Taking not already fulfilled connection between batch0 and 1
    open_connections: list[tuple[int, int]] = [c for c in batch0_connection + batch1_connection if c[1] not in inputs]
    double_connections: list[tuple[int, int]] = []
    batches: list[list[Operator]] = [batch0, batch1]


    # From open_connections, get nodes (potentially satisfiable)
    # In the nodes, check for input arity
    #  if 1, is satisfiable
    #  if 2, check in "double_connection_list" if there is already a connection there
    #       if yes, then satisfiable
    #       if not, add connection to "double_connection_list"
    while len(leftover_op) > 0:
        current_batch = []
        used_connections = []
        new_connections = []
        for c in open_connections:
            dest = c[1]
            op = get_operator_with_id(dest)

            def op_is_satisfiable(op: Operator, tipe: type) -> None:
                if t is not Output:
                    current_batch.append(op)
                    leftover_op.remove(op)

                if tipe in [Move, Transformer, Import, Merger]:
                    new_connections.append((op.operator_id, op.normal_output_dest))
                elif tipe in [Duplicate, Splitter]:
                    new_connections.append((op.operator_id, op.normal_output_dest))
                    new_connections.append((op.operator_id, op.special_output_dest))
                elif tipe in [Consumer, Output]:
                    pass
                else:
                    raise TypeError(f"Operator {op.operator_id} is not an operator")

            t = type(op)
            if t in [Move, Transformer, Duplicate, Splitter, Consumer, Output]:
                # Single input - directly satisfiable
                op_is_satisfiable(op, t)
            elif t in [Import, Merger]:
                # Double input - check for two connections
                if c[1] in [d for (o, d) in double_connections]:
                    op_is_satisfiable(op, t)
                    double_connections = [dc for dc in double_connections if dc[1] != c[1]]
                else:
                    double_connections.append(c)
            elif t in [Generator]:
                raise RuntimeError(f"Generator {dest} is a destination.")
            else:
                raise TypeError(f"Operator {dest} is not an operator")
            used_connections.append(c)

        open_connections = [oc for oc in open_connections if oc not in used_connections]
        open_connections.extend(new_connections.copy())
        batches.append(current_batch.copy())

    batches.append(batch9)

    # Potential Shrinking of the batches 0 and 1
    # TODO

    # Removing empty batches (notably generator, inputs and outputs)
    batches = [b for b in batches if b]

    return batches

class OperatorGraph:
    """
    TODO
    """
    def __init__(self,
                 operators: list[Operator],
                 inputs: list[OperatorId],
                 outputs: dict[OperatorId, PlaceId]
             ):
        self.batches: list[list[Operator]] = get_batches(operators, inputs)
        #self.inputs = inputs
        self.outputs = outputs

    def run(self, inputs: dict[OperatorId, Token]) -> dict[PlaceId, list[Token]]:
        """
        With given inputs, run them through the operators graph.

        Parameters
        ----------
        inputs: dict[OperatorId, Token]
            A map of OperatorId to a particular Token.

        Returns
        -------
        dict[PlaceId, list[Token]]
            A map of token to put into places (the map is reversed key-value wise for convenience).
        """
        def get_operator_index_for_packet(packet_: Packet) -> (int, int):
            """
            Find the position in batches of the destination of a packet.
            :param packet_: The packet whose destination we are looking for.
            :return: The batch number and the index in said batch.
            """
            for b_, _ in enumerate(self.batches):
                for i_, _ in enumerate(self.batches[b_]):
                    if self.batches[b_][i_].operator_id == packet_[0]:
                        return b_, i_
            raise RuntimeError(f"No operator found for packet {packet_}")

        # Interface from inputs (feeding inputs to first batch)
        for input_op_id in list(inputs.keys()):
            input_packet = (input_op_id, NORMAL_CHANNEL_ID, inputs.get(input_op_id))
            (b, i) = get_operator_index_for_packet(input_packet)
            self.batches[b][i].ingest_packet(input_packet)

        # Running all batches but the last
        for batch in self.batches[:-1]:
            for op in batch:
                new_packets = op.compute()
                for new_packet in new_packets:
                    (b, i) = get_operator_index_for_packet(new_packet)
                    # assert b > current batch
                    self.batches[b][i].ingest_packet(new_packet)

        # Interface to outputs (last batch has void destinations)
        dict_list_builder = DictListBuilder[PlaceId, Token]()
        for op in self.batches[-1]:
            output_tokens = op.compute()

            for output_token in output_tokens:
                dest: PlaceId = self.outputs[op.operator_id]
                token: Token = output_token[2]
                dict_list_builder.append(dest, token)

        # TODO
        #  Assert that every operator is empty
        return dict_list_builder.build()
