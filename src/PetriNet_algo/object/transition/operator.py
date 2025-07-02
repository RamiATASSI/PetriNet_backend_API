from abc import abstractmethod, ABC
from typing import Callable

from src.PetriNet_algo.data_structure.dict_list_builder import DictListBuilder
from src.PetriNet_algo.object.place import Place, PlaceId
from src.PetriNet_algo.object.token import Token, Attribute, AttributeK

"""A transformation/generator/selector function."""
type Transformation = Callable[[Token | None], Token]

"""The type for channel identification."""
type ChannelId = int
"""The ID of a void channel."""
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

########################################################################################################################
####################################################### Operator #######################################################
########################################################################################################################


class Operator(ABC):
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
                 special_output_dest: OperatorId = VOID_OUTPUT_ID,
                 transformation: Transformation = lambda token: token):
        self.operator_id = operator_id
        self.transformation = transformation

        self.normal_output_dest = normal_output_dest
        self.normal_input_channel: None | Token = None
        self.special_output_dest = special_output_dest
        self.special_input_channel: None | Token = None

    def ingest_packet(self, packet: Packet):
        assert packet[0] == self.operator_id
        if packet[1] == NORMAL_CHANNEL_ID:
            if self.normal_input_channel is None:
                self.normal_input_channel = packet[2]
            else:
                raise RuntimeError("Normal channel of operator {} is already occupied".format(self.operator_id))
        elif packet[1] == SPECIAL_CHANNEL_ID:
            if self.special_input_channel is None:
                self.special_input_channel = packet[2]
            else:
                raise RuntimeError("Special channel of operator {} is already occupied".format(self.operator_id))
        else:
            raise RuntimeError("Channel ID of packet {} is not valid".format(packet))

    def __clear__(self):
        self.normal_input_channel = None
        self.special_output_dest = None

    @abstractmethod
    def __compute__(self) -> list[Packet]:
        """
        TODO

        Return
        ------
        A tuple containing the Packet for the normal channel, and a Packet for the special channel.
        """
        pass

    @abstractmethod
    def __is_computable__(self) -> bool:
        """TODO"""
        pass

    def compute(self) -> list[Packet]:
        """
        TODO
        """
        if self.__is_computable__():
            produced_tokens = self.__compute__()
            self.__clear__()
            return produced_tokens
        else:
            # DEBUG: "Operator {} is not computable".format(self.operator_id)
            return []


class Move(Operator):
    def __init__(self, operator_id: OperatorId, normal_output_dest: OperatorId):
        super().__init__(operator_id, normal_output_dest)

    def __compute__(self) -> list[Packet]:
        assert self.special_input_channel is None
        return [(self.normal_output_dest, NORMAL_CHANNEL_ID, self.normal_input_channel)]

    def __is_computable__(self) -> bool:
        return self.normal_input_channel is not None and self.special_input_channel is None


class Transformer(Operator):
    def __init__(self, operator_id: OperatorId, normal_output_dest: OperatorId, transformation: Transformation):
        super().__init__(operator_id, normal_output_dest, transformation=transformation)

    def __compute__(self) -> list[Packet]:
        assert self.special_input_channel is None
        return [(self.normal_output_dest, NORMAL_CHANNEL_ID, self.transformation(self.normal_input_channel))]

    def __is_computable__(self) -> bool:
        return self.normal_input_channel is not None and self.special_input_channel is None


class Duplicate(Operator):
    def __init__(self, operator_id: OperatorId, special_output_dest: OperatorId):
        super().__init__(operator_id, special_output_dest)

    def __compute__(self) -> list[Packet]:
        return [
            (self.normal_output_dest,  NORMAL_CHANNEL_ID,  self.normal_input_channel),
            (self.special_output_dest, SPECIAL_CHANNEL_ID, self.normal_input_channel.copy()),
        ]

    def __is_computable__(self) -> bool:
        return self.normal_input_channel is not None and self.special_input_channel is None


class Import(Operator):
    """TODO"""
    def __init__(self, operator_id: OperatorId, special_output_dest: OperatorId, attribute_key_in: AttributeK, attribute_key_out: AttributeK):
        super().__init__(operator_id, special_output_dest)
        self.attribute_key_in = attribute_key_in
        self.attribute_key_out = attribute_key_out

    def __compute__(self) -> list[Packet]:
        token = self.normal_input_channel
        token_to_import_from = self.special_input_channel
        attribute_val = token_to_import_from.attributes[self.attribute_key]
        token.attributes[self.attribute_key] = attribute_val

        return [
            (self.normal_output_dest, NORMAL_CHANNEL_ID, token),
        ]

    def __is_computable__(self) -> bool:
        return self.normal_input_channel is not None and self.special_input_channel is not None


class Generator(Operator):
    def __init__(self, operator_id: OperatorId, normal_output_dest: OperatorId, generator: Transformation):
        super().__init__(operator_id, normal_output_dest, transformation=generator)

    def __compute__(self) -> list[Packet]:
        assert self.normal_input_channel is None
        assert self.special_input_channel is None
        return [(self.normal_output_dest, NORMAL_CHANNEL_ID, self.transformation(None))]

    def __is_computable__(self) -> bool:
        return self.normal_input_channel is None and self.special_input_channel is None


class Consumer(Operator):
    def __init__(self, operator_id: OperatorId, normal_output_dest: OperatorId):
        super().__init__(operator_id, normal_output_dest)

    def __compute__(self) -> list[Packet]:
        assert self.special_input_channel is None
        return list()

    def __is_computable__(self) -> bool:
        return self.normal_input_channel is not None and self.special_input_channel is None


class Merger(Operator):
    def __init__(self, operator_id: OperatorId, normal_output_dest: OperatorId, ordering: Callable[[list[Token]], None]):
        super().__init__(operator_id, normal_output_dest)
        self.ordering: Callable[[list[Token]], None] = ordering

    def __compute__(self) -> list[Packet]:
        assert self.special_input_channel.is_super_token()
        return [
            (self.normal_output_dest, NORMAL_CHANNEL_ID,
             self.special_input_channel.merge(self.normal_input_channel, self.ordering))
        ]

    def __is_computable__(self) -> bool:
        return self.normal_input_channel is not None and self.special_input_channel is not None


class Splitter(Operator):
    def __init__(self, operator_id: OperatorId, normal_output_dest: OperatorId, selector: Transformation):
        super().__init__(operator_id, normal_output_dest, transformation=selector)

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
    def __init__(self, operator_id: OperatorId, normal_output_dest: OperatorId, dest_place: PlaceId):
        super().__init__(operator_id, normal_output_dest)
        self.dest_place = dest_place

    def __compute__(self) -> list[Packet]:
        raise RuntimeError("An Output Operator {} is not computable".format(self.operator_id))

    def __is_computable__(self) -> bool:
        return False

    def retrieve(self) -> dict[PlaceId, Token]:
        """
        TODO
        """
        return dict([(self.dest_place, self.normal_input_channel)])


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



    # TODO Last batch should be the "output" operators.
    # TODO Update doc about above TODO.

    operator_number = len(operators)
    # Put generators in the first batch and input inside the second batch
    batches: list[list[Operator]] = [
        [operator for operator in operators if type(operator) is Generator],
        [operator for operator in operators if operator.operator_id in inputs]
    ]
    init_batches: list[Operator] = batches[0]
    init_batches.extend(batches[1])

    # Initialization of the algorithm
    leaf_connections: set[tuple[OperatorId, ChannelId]] = set()
    for op in init_batches:
        if type(op) in [Move, Transformer, Merger]:
            leaf_connections.add((op.normal_output_dest, NORMAL_CHANNEL_ID))
        elif type(op) is Splitter:
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
            elif type(potential_node) is Splitter:
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

    # TODO
    #  Assert all operators are in a batch
    #  Assert all outputs are in the last batch
    #  Assert No dependence in the first batch

    # TODO A compacter ?

    return batches


class OperatorGraph:
    """
    TODO
    """
    def __init__(self, operators: list[Operator], inputs: list[OperatorId], outputs: dict[OperatorId, PlaceId]):
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
        dict[Place, list[Token]]
            A map of token to put into places (the map is reversed key-value wise for convenience).
        """
        def get_operator_index_for_packet(packet_: Packet) -> (int, int):
            """
            Find the position in batches of the destination of a packet.
            :param packet_: The packet whose destination we are looking for.
            :return: The batch number and the index in said batch.
            """
            for b_ in range(len(self.batches)):
                for i_ in range(len(self.batches[b_])):
                    if self.batches[b_][i_].operator_id == packet_[0]:
                        return b_, i_
            raise RuntimeError("No operator found for packet {}".format(packet_))

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
