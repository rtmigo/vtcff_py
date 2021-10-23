# (c) 2021 Artёm IG <github.com/rtmigo>

from typing import Optional

from vtcff.filters.common import Scaling


class ZscaleCommand:

    def __init__(self):
        self._pairs = dict()
        self.scaling: Optional[Scaling] = None

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

    # w = -2:h = 2160

    def __str__(self):

        all_pairs = dict()
        if self.scaling is not None:
            if self.scaling.downscale_only:
                raise NotImplementedError
            all_pairs["filter"] = 'spline36'
            all_pairs["w"] = str(self.scaling.width)
            all_pairs["h"] = str(self.scaling.height)

        for k, v in self._pairs.items():
            all_pairs[k] = v

        if not all_pairs:
            return ''
        return "zscale=" + ":".join(
            lhs + '=' + rhs for (lhs, rhs) in all_pairs.items())


class ColorSpaces:
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
