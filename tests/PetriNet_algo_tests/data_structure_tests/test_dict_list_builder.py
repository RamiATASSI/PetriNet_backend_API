import unittest

from PetriNet_algo.data_structure.dict_list_builder import DictListBuilder

class DictListBuilderTest(unittest.TestCase):
    def test_dict_list_builder_append(self):
        d = DictListBuilder[int, int]()
        d.append(1, 10)
        d.append(1, 10)
        d.append(1, 10)
        d.append(1, 11)
        d.append(1, 12)
        d.append(2, 20)
        d.append(2, 21)
        d.append(3, 30)
        d.append(3, 30)
        d.append(3, 30)
        d.append(4, 40)
        d.append(4, 41)
        d.append(4, 42)
        d.append(4, 43)

        self.assertListEqual(d.get(1), [10, 10, 10, 11, 12])
        self.assertListEqual(d.get(2), [20, 21])
        self.assertListEqual(d.get(3), [30, 30, 30])
        self.assertListEqual(d.get(4), [40, 41, 42, 43])

    def test_dict_list_builder_append_all(self):
        d = DictListBuilder[int, int]()
        d.append_all(1, [10, 11, 12])
        d.append_all(1, [10, 11, 12])
        d.append_all(2, [20, 21])
        d.append_all(3, [30])
        d.append_all(3, [30])
        d.append_all(4, [40, 41, 42, 43])

        self.assertListEqual(d.get(1), [10, 11, 12, 10, 11, 12])
        self.assertListEqual(d.get(2), [20, 21])
        self.assertListEqual(d.get(3), [30, 30])
        self.assertListEqual(d.get(4), [40, 41, 42, 43])

    def test_dict_list_builder_append_map(self):
        d = DictListBuilder[int, int]()

        m: dict[int, list[int]] = dict([
            (1, [10, 11, 12]),
            (2, [20, 21]),
            (3, [30, 30]),
            (4, [40, 41, 42, 43])
        ])

        d.append_map(m)

        self.assertListEqual(d.get(1), [10, 11, 12])
        self.assertListEqual(d.get(2), [20, 21])
        self.assertListEqual(d.get(3), [30, 30])
        self.assertListEqual(d.get(4), [40, 41, 42, 43])

    def test_dict_list_builder_remove(self):
        d = DictListBuilder[int, int]()
        d.append(1, 10)
        d.append_all(2, [20, 21, 22])

        d.remove(1, 10)
        d.remove(2, 21)

        self.assertFalse(d.contains(1))
        self.assertListEqual(d.get(2), [20, 22])
        self.assertRaises(ValueError, d.remove, 2, 21)
        self.assertRaises(KeyError, d.get, 3)

    def test_dict_list_builder_remove_all(self):
        d = DictListBuilder[int, int]()
        d.append_all(1, [10, 11, 12])
        d.append_all(2, [20, 21])
        d.append_all(3, [30])
        d.append_all(4, [40, 41, 42, 43])

        d.remove_all(1, [10, 11, 12])
        d.remove_all(3, [30])
        d.remove_all(4, [40, 42])

        self.assertFalse(d.contains(1))
        self.assertListEqual(d.get(2), [20, 21])
        self.assertRaises(ValueError, d.remove_map, dict([(2, [22])]))
        self.assertFalse(d.contains(3))
        self.assertRaises(KeyError, d.remove_map, dict([(3, [30])]))
        self.assertListEqual(d.get(4), [41, 43])

    def test_dict_list_builder_remove_map(self):
        d = DictListBuilder[int, int]()
        d.append_all(1, [10, 11, 12])
        d.append_all(2, [20, 21])
        d.append_all(3, [30])
        d.append_all(4, [40, 41, 42, 43])

        m: dict[int, list[int]] = dict([
            (1, [10, 11, 12]),
            (3, [30]),
            (4, [40, 42])
        ])

        d.remove_map(m)

        self.assertFalse(d.contains(1))
        self.assertListEqual(d.get(2), [20, 21])
        self.assertRaises(ValueError, d.remove_map, dict([(2, [22])]))
        self.assertFalse(d.contains(3))
        self.assertRaises(KeyError, d.remove_map, dict([(3, [30])]))
        self.assertListEqual(d.get(4), [41, 43])


    def test_dict_list_builder_contains(self):
        d = DictListBuilder[int, int]()
        d.append_all(1, [10, 11, 12])
        d.append_all(2, [20, 21, 21])

        self.assertFalse(d.contains(0))
        self.assertTrue(d.contains(1))
        self.assertTrue(d.contains(2))
        self.assertFalse(d.contains(3))

    def test_dict_list_builder_verify_immutability_after_build(self):
        d = DictListBuilder[int, int]()
        d.append_all(1, [10, 11, 12, 13, 14, 15])
        d_build: dict[int, list[int]] = d.build()
        d.append(1,16)
        d.append(2, 20)
        self.assertListEqual(d_build[1], [10, 11, 12,13, 14, 15])
        self.assertListEqual(d.get(1), [10, 11, 12, 13, 14, 15, 16])
        self.assertListEqual(d.get(2), [20])

    def test_dict_list_builder_merge(self):
        d1 = DictListBuilder[int, int]()
        d1.append_all(1, [10, 11, 12])
        d1.append_all(2, [20, 21, 22])
        d2 = DictListBuilder[int, int]()
        d2.append_all(1, [10, 11, 12])
        d2.append_all(3, [30, 31, 32])

        d1.merge_with(d2)

        self.assertListEqual(d1.get(1), [10, 11, 12, 10, 11, 12])
        self.assertListEqual(d1.get(2), [20, 21, 22])
        self.assertListEqual(d1.get(3), [30, 31, 32])

if __name__ == '__main__':
    unittest.main()
