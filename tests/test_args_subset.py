import unittest

from vtcff._args_subset import ArgsSubset


class TestArgsSubset(unittest.TestCase):
    def test_args_list_ok(self):
        las = ArgsSubset()
        las.list.extend(['aaa', 'b b b', 'ccc'])
        self.assertEqual(las.string, "aaa 'b b b' ccc")

    def test_string(self):
        las = ArgsSubset()
        las.string = "something"
        self.assertEqual(las.string, "something")

    def test_pairs(self):
        las = ArgsSubset()
        las.string = "-a 1 -b 2"
        self.assertEqual(list(las.pairs()), [('-a', '1'), ('-b', '2')])

    def test_pairs_empty(self):
        las = ArgsSubset()
        las.string = ""
        self.assertEqual(list(las.pairs()), [])

    def test_pairs_no_value(self):
        las = ArgsSubset()
        las.string = "-a 1 -b -c -d 2"
        self.assertEqual(list(las.pairs()),
                         [('-a', '1'), ('-b', None), ('-c', None), ('-d', '2')])

    def test_pairs_no_key(self):
        las = ArgsSubset()
        las.string = "-a 1 2"
        with self.assertRaises(ValueError):
            list(las.pairs())