# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from typing import Optional

from vtcff._common import Scale, frame_dimension_spec
from vtcff._filter_base import FilterBase


def _bool_to_full_limited_none(x: Optional[bool]):
    if x is None:
        return None
    elif x:
        return "full"
    else:
        return "limited"


def _full_limited_none(x: Optional[str]):
    if x is None:
        return None
    elif x == "full":
        return True
    elif x == "limited":
        return False
    else:
        raise ValueError


class ZscaleFilter(FilterBase):
    def __init__(self):
        super().__init__()
        self.scaling: Optional[Scale] = None

    @property
    def dst_range_full(self) -> Optional[bool]:
        return _full_limited_none(self._pairs.get('range'))

    @dst_range_full.setter
    def dst_range_full(self, x: Optional[bool]):
        self._set_or_remove('range',
                            _bool_to_full_limited_none(x))

    @property
    def src_range_full(self) -> Optional[bool]:
        return _full_limited_none(self._pairs.get('rangein'))

    @src_range_full.setter
    def src_range_full(self, x: Optional[bool]):
        self._set_or_remove('rangein',
                            _bool_to_full_limited_none(x))

    @property
    def dst_matrix(self) -> Optional[str]:
        return self._pairs.get('matrix')

    @dst_matrix.setter
    def dst_matrix(self, val: Optional[str]):
        self._set_or_remove('matrix', val)

    @property
    def src_matrix(self) -> Optional[str]:
        # todo test
        return self._pairs.get('matrixin')

    @src_matrix.setter
    def src_matrix(self, val: Optional[str]):
        # todo test
        self._set_or_remove('matrixin', val)

    # w = -2:h = 2160

    def __str__(self):

        all_pairs = dict()
        if self.scaling is not None:
            all_pairs["filter"] = 'spline36'
            # todo test downscale_only
            all_pairs["w"] = frame_dimension_spec(
                iw_or_ih='iw',
                value=self.scaling.width,
                downscale_only=self.scaling.downscale_only)
            all_pairs["h"] = frame_dimension_spec(
                iw_or_ih='ih',
                value=self.scaling.height,
                downscale_only=self.scaling.downscale_only)

        for k, v in self._pairs.items():
            all_pairs[k] = v

        if not all_pairs:
            return ''

        all_pairs['dither'] = 'error_diffusion'

        return "zscale=" + ":".join(
            lhs + '=' + rhs for (lhs, rhs) in all_pairs.items())


class ColorSpaces:
    # http://underpop.online.fr/f/ffmpeg/help/zscale.htm.gz
    _data = [
        # left ffmpeg, right zscale

        ('bt709', '709'),

        # ffmpeg bt470bg is BT.470BG or BT.601-6 625
        # (http://underpop.online.fr/f/ffmpeg/help/colorspace.htm.gz)
        ('bt470bg', '470bg'),

        # ffmpeg smpte170m is SMPTE-170M or BT.601-6 525
        # (http://underpop.online.fr/f/ffmpeg/help/colorspace.htm.gz)
        ('smpte170m', '170m'),

        # ffmpeg bt2020ncl is BT.2020 with non-constant luminance
        # (http://underpop.online.fr/f/ffmpeg/help/colorspace.htm.gz)
        ('bt2020ncl', '2020_ncl'),

        # todo test ('bt2020' is 8 bit only?)
        # bt2020 - BT.2020
        # bt2020-10 - BT.2020 for 10-bits content
        # bt2020-12 - BT.2020 for 12-bits content
        ('bt2020', '2020_cl'),
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
