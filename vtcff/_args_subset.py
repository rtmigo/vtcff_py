# (c) 2021 Artёm IG <github.com/rtmigo>

import shlex
import unittest
from typing import List, Iterable, Tuple, Optional


class ArgsSubset:
    def __init__(self):
        self.list: List[str] = list()

    @property
    def string(self) -> str:
        return shlex.join(self.list)

    @string.setter
    def string(self, value: str):
        self.list = shlex.split(value)

    def pairs(self) -> Iterable[Tuple[str, Optional[str]]]:

        def is_key(s):
            return s.startswith('-')

        prev_key = None
        for arg in self.list:
            if prev_key is None:
                if is_key(arg):
                    prev_key = arg
                    continue
                else:
                    raise ValueError(arg)

            else:
                assert prev_key is not None
                if is_key(arg):
                    yield prev_key, None
                    prev_key = arg
                else:
                    assert prev_key is not None and not is_key(arg)
                    yield prev_key, arg
                    prev_key = None

        if prev_key is not None:
            yield prev_key, None


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
