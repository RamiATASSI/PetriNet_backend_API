import unittest

from PetriNet_algo.data_structure.dict_list_builder import DictListBuilder

if __name__ == '__main__':
    unittest.main()

class DictListBuilderTest(unittest.TestCase):
    def test_dict_list_builder_append(self):
        d = DictListBuilder[int, int]()

        d.append(1, 10)
        d.append(1, 11)
        d.append(1, 12)

        d.append(2, 20)
        d.append(2, 21)

        d.append(3, 30)

        d.append(4, 40)
        d.append(4, 41)
        d.append(4, 42)
        d.append(4, 43)

        self.assertListEqual(d.get(1), [10, 11, 12])
        self.assertListEqual(d.get(2), [20, 21])
        self.assertListEqual(d.get(3), [30])
        self.assertListEqual(d.get(4), [40, 41, 42, 43])
        self.assertRaises()

    def test_dict_list_builder_append_all(self):
        d = DictListBuilder[int, int]()

        d.append_all(1, [10, 11, 12])

        d.append_all(2, [20, 21])

        d.append_all(3, [30])

        d.append_all(4, [40, 41, 42, 43])

        self.assertListEqual(d.get(1), [10, 11, 12])
        self.assertListEqual(d.get(2), [20, 21])
        self.assertListEqual(d.get(3), [30])
        self.assertListEqual(d.get(4), [40, 41, 42, 43])

    def test_dict_list_builder_verify_immutability_after_build(self):

        pass
