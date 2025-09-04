import unittest

from PetriNet_algo.object.token import SimpleToken, TokenType, Token, SuperToken
from PetriNet_algo.object.transition.operator import Move, Transformer, Duplicate, Import, \
    Generator, Consumer, Merger, Splitter, Output, VOID_CHANNEL_ID, NORMAL_CHANNEL_ID, Operator, \
    OperatorId, SPECIAL_CHANNEL_ID, Packet


class OperatorTest(unittest.TestCase):
    def check_op_is_clear(self, op: Operator):
        """Checks that both input channels are empty."""
        self.assertEqual(None, op.normal_input_channel)
        self.assertEqual(None, op.special_input_channel)

    def check_init(self,  op: Operator, expected_id: OperatorId, expected_normal_output_dest: OperatorId, expected_special_output_dest: OperatorId):
        """
        Checks that an operator was correctly initialized
        - No tokens in input channels
        - Correct values for ID and destination
        """
        self.check_op_is_clear(op)

        self.assertEqual(expected_id, op.operator_id)

        # Correct input channels
        self.assertEqual(expected_normal_output_dest, op.normal_output_dest)
        self.assertEqual(expected_special_output_dest, op.special_output_dest)

    def assertEqualToken(self, first: Token, second: Token):
        match (first, second):
            case (SimpleToken(), SimpleToken()):
                self.assertEqual(first.token_type, second.token_type)
                self.assertEqual(first.attributes, second.attributes)
            case (SuperToken(), SuperToken()):
                self.assertEqual(first.token_type, second.token_type)
                self.assertEqual(first.attributes, second.attributes)
                print(first.components)
                for t1, t2 in zip(first.components, second.components):
                    self.assertEqualToken(t1, t2)
            case (_, _):
                raise AssertionError(f"Token {first} and {second} are not the same type")

    def assertEqualPacket(self, first: Packet, second: Packet):
        self.assertEqual(first[0], second[0])
        self.assertEqual(first[1], second[1])
        self.assertEqualToken(first[2], second[2])

    def test_move(self):
        t = SimpleToken(TokenType("BasicMove"), {})
        op_id, out_norm_id = 10, 11
        op = Move(op_id, out_norm_id)

        self.check_init(op, op_id, out_norm_id, VOID_CHANNEL_ID)

        op.ingest_packet( (op_id, NORMAL_CHANNEL_ID, t) )
        self.assertEqual(t, op.normal_input_channel)
        self.assertEqual(None, op.special_input_channel)

        p = op.compute()
        self.assertEqual(len(p), 1)
        self.assertEqualPacket(p[0], (out_norm_id, NORMAL_CHANNEL_ID, t) )

        self.check_op_is_clear(op)

    def test_transformer(self):
        basic = TokenType("BasicTransformer")
        new_name = "NewName"
        t = SimpleToken(basic, {'name': (str, "MyName")})
        op_id, out_norm_id = 10, 11

        def transformation(token: Token) -> Token:
            token.attributes['name'] = (str, new_name)
            return token
        op = Transformer(op_id, out_norm_id, transformation)

        self.check_init(op, op_id, out_norm_id, VOID_CHANNEL_ID)

        op.ingest_packet((op_id, NORMAL_CHANNEL_ID, t))
        self.assertEqual(t, op.normal_input_channel)
        self.assertEqual(None, op.special_input_channel)

        p = op.compute()
        self.assertEqual(len(p), 1)
        self.assertEqualPacket(p[0], (out_norm_id, NORMAL_CHANNEL_ID, SimpleToken(basic, {'name': (str, new_name)})))

        self.check_op_is_clear(op)

    def test_duplicate(self):
        t = SimpleToken(TokenType("BasicDuplicate"), {'name': (str, "MyName")})
        op_id, out_norm_id, out_spec_id = 10, 11, 12
        op = Duplicate(op_id, out_norm_id, out_spec_id)

        self.check_init(op, op_id, out_norm_id, out_spec_id)

        op.ingest_packet( (op_id, NORMAL_CHANNEL_ID, t) )
        self.assertEqual(t, op.normal_input_channel)
        self.assertEqual(None, op.special_input_channel)

        p = op.compute()
        self.assertEqual(len(p), 2)
        self.assertEqualPacket(p[0], (out_norm_id, NORMAL_CHANNEL_ID, t) )
        self.assertEqualPacket(p[1], (out_spec_id, SPECIAL_CHANNEL_ID, t) )

        self.check_op_is_clear(op)

    def test_import(self):
        ttype = TokenType("BasicImport")
        t_to = SimpleToken(ttype, {'name1': (str, "MyName")})
        t_from = SimpleToken(ttype, {'name2': (str, "OtherName")})
        op_id, out_norm_id= 10, 11
        op = Import(op_id, out_norm_id, 'name2', 'name1')

        self.check_init(op, op_id, out_norm_id, VOID_CHANNEL_ID)

        op.ingest_packet( (op_id, NORMAL_CHANNEL_ID, t_to) )
        op.ingest_packet( (op_id, SPECIAL_CHANNEL_ID, t_from) )
        self.assertEqual(t_to, op.normal_input_channel)
        self.assertEqual(t_from, op.special_input_channel)

        p = op.compute()
        self.assertEqual(len(p), 1)
        self.assertEqualPacket(p[0], (out_norm_id, NORMAL_CHANNEL_ID, SimpleToken(ttype, {'name1': (str, "OtherName")})) )

        self.check_op_is_clear(op)

    def test_generator(self):
        t = SimpleToken(TokenType("BasicGenerator"), {'name': (str, "MyName")})
        def generator(a: None) -> Token:
            return t
        op_id, out_norm_id = 10, 11
        op = Generator(op_id, out_norm_id, generator)

        self.check_init(op, op_id, out_norm_id, VOID_CHANNEL_ID)

        p = op.compute()
        self.assertEqual(len(p), 1)
        # Verify packet
        self.assertEqualPacket(p[0], (out_norm_id, NORMAL_CHANNEL_ID, t))

        self.check_op_is_clear(op)

    def test_consumer(self):
        t = SimpleToken(TokenType("BasicConsumer"), {'name': (str, "MyName")})

        op_id = 10
        op = Consumer(op_id)

        self.check_init(op, op_id, VOID_CHANNEL_ID, VOID_CHANNEL_ID)

        op.ingest_packet( (op_id, NORMAL_CHANNEL_ID, t) )
        self.assertEqual(t, op.normal_input_channel)

        p = op.compute()
        self.assertEqual(len(p), 0)

        self.check_op_is_clear(op)

    def test_merger(self):
        ttype = TokenType("BasicMerger")
        t_simple = SimpleToken(ttype, {'name': (str, "MyName2")})
        t_super = SuperToken(ttype, {'name': (str, "MyName")}, [
            SimpleToken(ttype, {'name': (str, "MyName1")}),
            SimpleToken(ttype, {'name': (str, "MyName3")}),
            SimpleToken(ttype, {'name': (str, "MyName4")})
        ])
        t_expected = SuperToken(ttype, {'name': (str, "MyName")}, [
            SimpleToken(ttype, {'name': (str, "MyName1")}),
            SimpleToken(ttype, {'name': (str, "MyName2")}),
            SimpleToken(ttype, {'name': (str, "MyName3")}),
            SimpleToken(ttype, {'name': (str, "MyName4")})
        ])
        def ordering(token: Token) -> None:
            token.components.sort(key=lambda st: st.attributes['name'])
        op_id, out_norm_id, out_spec_id = 10, 11, 12
        op = Merger(op_id, out_norm_id, ordering)

        self.check_init(op, op_id, out_norm_id, VOID_CHANNEL_ID)

        op.ingest_packet((op_id, NORMAL_CHANNEL_ID, t_simple))
        op.ingest_packet((op_id, SPECIAL_CHANNEL_ID, t_super))
        self.assertEqual(t_simple, op.normal_input_channel)
        self.assertEqual(t_super, op.special_input_channel)

        p = op.compute()
        self.assertEqual(len(p), 1)
        print("=====", p[0], "=====", p[0][2].components)
        self.assertEqualPacket(p[0], (out_norm_id, NORMAL_CHANNEL_ID, t_expected))

        self.check_op_is_clear(op)

    def test_splitter(self):
        ttype = TokenType("BasicSplitter")
        t_super = SuperToken(ttype, {'name': (str, "MyName")}, [
            SimpleToken(ttype, {'name': (str, "MyName1")}),
            SimpleToken(ttype, {'name': (str, "MyName2")}),
            SimpleToken(ttype, {'name': (str, "MyName3")}),
            SimpleToken(ttype, {'name': (str, "MyName4")})
        ])
        t_out = SimpleToken(ttype, {'name': (str, "MyName2")})
        t_expected = SuperToken(ttype, {'name': (str, "MyName")}, [
            SimpleToken(ttype, {'name': (str, "MyName1")}),
            SimpleToken(ttype, {'name': (str, "MyName3")}),
            SimpleToken(ttype, {'name': (str, "MyName4")})
        ])
        def selector(token: Token) -> Token:
            out = token.components[1]
            return out
        op_id, out_norm_id, out_spec_id = 10, 11, 12
        op = Splitter(op_id, out_norm_id, out_spec_id, selector)

        self.check_init(op, op_id, out_norm_id, out_spec_id)

        op.ingest_packet((op_id, NORMAL_CHANNEL_ID, t_super))
        self.assertEqual(t_super, op.normal_input_channel)

        p = op.compute()
        self.assertEqual(len(p), 2)
        self.assertEqualPacket(p[0], (out_norm_id, NORMAL_CHANNEL_ID, t_out))
        self.assertEqualPacket(p[1], (out_spec_id, SPECIAL_CHANNEL_ID, t_expected))

        self.check_op_is_clear(op)

    def test_output(self):
        # TODO
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
