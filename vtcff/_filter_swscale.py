# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from typing import Optional

from vtcff._filter_base import FilterBase
from vtcff._filter_zscale import _full_limited_none, _bool_to_full_limited_none


class SwscaleFilter(FilterBase):
    # it seems, there are at least three ways to convert colors with swscale:
    #   -vf "scale=out_color_matrix..."
    #   -vf "colormatrix=..."
    #   -vf "colorspace=..."
    #
    # https://trac.ffmpeg.org/wiki/colorspace compares "colorspace"
    # and "colormatrix" (2019): "colormatrix produces horrible quality
    # for anything > 8bpc, while colorspace produces something decent,
    # at least for 10bpc. For 8bpc they both produce similar bad quality
    # probably due to improper design in the algorithms. For 8bpc
    # colorspace still seems to produce slightly better quality than
    # colormatrix"
    #
    # However, even if we always preferred `colorspace`, it is not clear how
    # to deal with the color range conversion (full/limited) that is only
    # done with "scale=" (or not?)
    #
    # In general, we choose the simplest way: we use the arguments of the
    # "scale=" filter in the hope that swscale developers will eventually
    # figure out how best to carry out this conversion.
    #
    # But at every opportunity, we prefer not to use this object and
    # swscale at all (zscale seems to be much more predictable)

    def __init__(self):
        super().__init__()
        self.width: Optional[int] = None
        self.height: Optional[int] = None
        self.downscale_only = False

    @property
    def dst_range_full(self) -> Optional[bool]:
        return _full_limited_none(self._pairs.get('out_range'))

    @dst_range_full.setter
    def dst_range_full(self, x: Optional[bool]):
        self._set_or_remove('out_range',
                            _bool_to_full_limited_none(x))

    @property
    def src_range_full(self) -> Optional[bool]:
        return _full_limited_none(self._pairs.get('in_range'))

    @src_range_full.setter
    def src_range_full(self, x: Optional[bool]):
        self._set_or_remove('in_range',
                            _bool_to_full_limited_none(x))

    @property
    def dst_matrix(self) -> Optional[str]:
        # todo test
        return self._pairs.get('out_color_matrix')

    @dst_matrix.setter
    def dst_matrix(self, val: Optional[str]):
        # todo test
        self._set_or_remove('out_color_matrix', val)

    @property
    def src_matrix(self) -> Optional[str]:
        # todo test
        return self._pairs.get('in_color_matrix')

    @src_matrix.setter
    def src_matrix(self, val: Optional[str]):
        # todo test
        self._set_or_remove('in_color_matrix', val)

    def __str__(self) -> str:
        final_pairs = dict(self._pairs)
        if self.downscale_only:
            if self.width is not None:
                final_pairs["width"] = (f"'min(iw,{self.width})'"
                                        if self.width > 0 else str(self.width))
            if self.height is not None:
                final_pairs["height"] = (f"'min(ih,{self.height})'"
                                         if self.height > 0 else str(
                    self.height))
        else:
            final_pairs["width"] = str(self.width)
            final_pairs["height"] = str(self.height)
        return self._to_string("scale", final_pairs.items())
