from __future__ import annotations

from enum import Enum
from typing import Union


class ColorSpace(Enum):
    # todo use in command
    bt709 = "bt709"

    # ffmpeg bt470bg is BT.470BG or BT.601-6 625
    # (http://underpop.online.fr/f/ffmpeg/help/colorspace.htm.gz)
    bt470bg = "bt470bg"
    """BT.470BG or BT.601-6 625"""

    # ffmpeg smpte170m is SMPTE-170M or BT.601-6 525
    # (http://underpop.online.fr/f/ffmpeg/help/colorspace.htm.gz)
    smpte170m = "smpte170m",
    """BT.601-6 525"""

    # ffmpeg bt2020ncl is BT.2020 with non-constant luminance
    # (http://underpop.online.fr/f/ffmpeg/help/colorspace.htm.gz)
    bt2020ncl = 'bt2020ncl'
    """BT.2020 with non-constant luminance"""

    # not tested yet (not sure how to implement)
    # bt2020 - BT.2020
    # bt2020-10 - BT.2020 for 10-bits content
    # bt2020-12 - BT.2020 for 12-bits content


def safe_str_to_colorspace(s: str) -> Union[ColorSpace, str]:
    try:
        return ColorSpace(s)
    except ValueError:
        return s


def safe_colorspace_to_str(cs: Union[ColorSpace, str]) -> str:
    if isinstance(cs, ColorSpace):
        return cs.value
    else:
        return str(cs)
