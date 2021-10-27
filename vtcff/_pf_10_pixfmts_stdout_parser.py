# SPDX-FileCopyrightText: (c) 2016-2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

import subprocess
import sys
from typing import Iterable, List, NamedTuple, Optional, Dict


def _pix_fmts_lines() -> Iterable[str]:
    result = subprocess.run(["ffmpeg", "-pix_fmts"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            encoding=sys.stdout.encoding or "utf-8")
    if result.returncode != 0:
        raise subprocess.CalledProcessError

    txt = result.stdout

    # txt is something like
    #
    # Pixel formats:
    # I.... = Supported Input  format for conversion
    # .O... = Supported Output format for conversion
    # ..H.. = Hardware accelerated format
    # ...P. = Paletted format
    # ....B = Bitstream format
    # FLAGS NAME            NB_COMPONENTS BITS_PER_PIXEL
    # -----
    # IO... yuv420p                3            12
    # IO... yuyv422                3            16
    # IO... rgb24                  3            24
    # IO... bgr24                  3            24
    # IO... yuv422p                3            16

    started = False

    returned = 0

    for line in txt.splitlines():

        if started:
            returned += 1
            yield line
        elif line == "-----":
            started = True

    if returned <= 10:
        raise ValueError(f"Failed to split output to lines. Output: {txt}")


class PixfmtOutputSpec(NamedTuple):
    flags: str
    name: str
    nb_components: int
    bits_per_pixel: int


def _pix_fmts_tuples() -> List[PixfmtOutputSpec]:
    result = list()
    for line in _pix_fmts_lines():
        words = line.split()
        pfo = PixfmtOutputSpec(words[0], words[1], int(words[2]),
                               int(words[3]))
        result.append(pfo)
    return result


_pix_format_spec: Optional[Dict[str, PixfmtOutputSpec]] = None


def pixfmt_to_spec(name: str) -> PixfmtOutputSpec:
    """Returns a particular parsed line of `ffmpeg -pix_fmts`"""
    global _pix_format_spec
    if _pix_format_spec is None:
        _pix_format_spec = dict()
        for t in _pix_fmts_tuples():
            _pix_format_spec[t.name] = t
    assert _pix_format_spec is not None
    return _pix_format_spec[name]
