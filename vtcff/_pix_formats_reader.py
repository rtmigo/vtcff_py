import subprocess
import sys
from typing import Iterable, List, NamedTuple, Optional, Dict


# перенесено в vtcff

def _pix_fmts_lines() -> Iterable[str]:
    txt = subprocess.check_output(["ffmpeg", "-pix_fmts"],
                                  stderr=subprocess.PIPE,
                                  encoding=sys.stdout.encoding or "utf-8")

    # if isinstance(txt, bytes):
    #   txt = txt.decode(sys.stdout.encoding)

    # там что-то вроде:
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


class PixelFormatOutput(NamedTuple):
    flags: str
    name: str
    nb_components: int
    bits_per_pixel: int


def _pix_fmts_tuples() -> List[PixelFormatOutput]:
    result = list()
    for line in _pix_fmts_lines():
        words = line.split()
        pfo = PixelFormatOutput(words[0], words[1], int(words[2]),
                                int(words[3]))
        result.append(pfo)
    return result


_pix_format_spec: Optional[Dict[str, PixelFormatOutput]] = None


def pix_format_spec(name: str) -> PixelFormatOutput:
    """Returns a particular parsed line of `ffmpeg -pix_fmts`"""
    global _pix_format_spec
    if _pix_format_spec is None:
        _pix_format_spec = dict()
        for t in _pix_fmts_tuples():
            _pix_format_spec[t.name] = t
    assert _pix_format_spec is not None
    return _pix_format_spec[name]
