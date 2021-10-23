import unittest
from typing import Optional


class ZscaleCommand:

    def __init__(self):
        self._pairs = dict()

    def _set_or_remove(self, key: str, val: Optional[str]):
        if val is not None:
            self._pairs[key] = val
        else:
            assert val is None
            if key in self._pairs:
                del self._pairs[key]
        assert self._pairs.get(key) == val

    # def range_full_to_limited(self):
    #     self._pairs['rangein'] = "full"
    #     self._pairs['range'] = "limited"

    @staticmethod
    def _full_limited_none(x: Optional[str]):
        if x is None:
            return None
        elif x == "full":
            return True
        elif x == "limited":
            return False
        else:
            raise ValueError

    @staticmethod
    def _bool_to_full_limited_none(x: Optional[bool]):
        if x is None:
            return None
        elif x:
            return "full"
        else:
            return "limited"


    @property
    def dst_range_full(self) -> Optional[bool]:
        return self._full_limited_none(self._pairs.get('range'))

    @dst_range_full.setter
    def dst_range_full(self, x: Optional[bool]):
        self._set_or_remove('range',
                            self._bool_to_full_limited_none(x))


    @property
    def src_range_full(self) -> Optional[bool]:
        return self._full_limited_none(self._pairs.get('rangein'))

    @src_range_full.setter
    def src_range_full(self, x: Optional[bool]):
        self._set_or_remove('rangein',
                            self._bool_to_full_limited_none(x))



    @property
    def dst_matrix(self) -> Optional[str]:
        return self._pairs.get('matrix')

    @dst_matrix.setter
    def dst_matrix(self, val: Optional[str]):
        self._set_or_remove('matrix', val)

    def __str__(self):
        if not self._pairs:
            return ''
        return "zscale=" + ":".join(
            lhs + '=' + rhs for (lhs, rhs) in self._pairs.items())


class TestZscaleCommand(unittest.TestCase):
    def test_empty(self):
        z = ZscaleCommand()
        self.assertEqual(str(z), '')

    def test_full_to_limited(self):
        z = ZscaleCommand()
        z.src_range_full = True
        z.dst_range_full = False
        self.assertEqual(str(z), 'zscale=rangein=full:range=limited')

    def test_709_plus(self):
        z = ZscaleCommand()
        #z.range_full_to_limited()
        z.dst_matrix = '709'
        self.assertEqual(str(z), 'zscale=matrix=709')

#    def test_709(self):
        # z = ZscaleCommand()
        # self.assertEqual(z.)
        # z.range_full_to_limited()
        # z.dst_matrix = '709'
        # self.assertEqual(str(z), 'zscale=rangein=full:range=limited:matrix=709')

class ZscaleColorSpaces:
    _data = [
        ('bt709', '709'),
        (None, None)
    ]

    @classmethod
    def ffmpeg_to_zscale(cls, cs):
        try:
            return next(z for (f, z) in cls._data if f == cs)
        except StopIteration:
            raise ValueError(cs)

    @classmethod
    def zscale_to_ffmpeg(cls, cs):
        try:
            return next(f for (f, z) in cls._data if z == cs)
        except StopIteration:
            raise ValueError(cs)