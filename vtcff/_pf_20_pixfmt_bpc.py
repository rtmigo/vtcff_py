# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

"""
It would probably be easier and more reliable to create a table with all pixel
formats. But I was too lazy. Therefore, below is a heuristic parser of the data
printed by the command "ffmpeg -pix_fmts".

The `_pix_format_to_depth` dictionary allows you to overload the parser
results with constants.

================================================================================

ffmpeg -pix_fmts

Pixel formats:
I.... = Supported Input  format for conversion
.O... = Supported Output format for conversion
..H.. = Hardware accelerated format
...P. = Paletted format
....B = Bitstream format
FLAGS NAME            NB_COMPONENTS BITS_PER_PIXEL
-----
IO... yuv420p                3            12
IO... yuyv422                3            16
IO... rgb24                  3            24
IO... bgr24                  3            24
IO... yuv422p                3            16
IO... yuv444p                3            24
IO... yuv410p                3             9
IO... yuv411p                3            12
IO... gray                   1             8
IO..B monow                  1             1
IO..B monob                  1             1
I..P. pal8                   1             8
IO... yuvj420p               3            12
IO... yuvj422p               3            16
IO... yuvj444p               3            24
IO... uyvy422                3            16
..... uyyvyy411              3            12
IO... bgr8                   3             8
.O..B bgr4                   3             4
IO... bgr4_byte              3             4
IO... rgb8                   3             8
.O..B rgb4                   3             4
IO... rgb4_byte              3             4
IO... nv12                   3            12
IO... nv21                   3            12
IO... argb                   4            32
IO... rgba                   4            32
IO... abgr                   4            32
IO... bgra                   4            32
IO... gray16be               1            16
IO... gray16le               1            16
IO... yuv440p                3            16
IO... yuvj440p               3            16
IO... yuva420p               4            20
IO... rgb48be                3            48
IO... rgb48le                3            48
IO... rgb565be               3            16
IO... rgb565le               3            16
IO... rgb555be               3            15
IO... rgb555le               3            15
IO... bgr565be               3            16
IO... bgr565le               3            16
IO... bgr555be               3            15
IO... bgr555le               3            15
..H.. vaapi_moco             0             0
..H.. vaapi_idct             0             0
..H.. vaapi_vld              0             0
IO... yuv420p16le            3            24
IO... yuv420p16be            3            24
IO... yuv422p16le            3            32
IO... yuv422p16be            3            32
IO... yuv444p16le            3            48
IO... yuv444p16be            3            48
..H.. dxva2_vld              0             0
IO... rgb444le               3            12
IO... rgb444be               3            12
IO... bgr444le               3            12
IO... bgr444be               3            12
IO... ya8                    2            16
IO... bgr48be                3            48
IO... bgr48le                3            48
IO... yuv420p9be             3            13
IO... yuv420p9le             3            13
IO... yuv420p10be            3            15
IO... yuv420p10le            3            15
IO... yuv422p10be            3            20
IO... yuv422p10le            3            20
IO... yuv444p9be             3            27
IO... yuv444p9le             3            27
IO... yuv444p10be            3            30
IO... yuv444p10le            3            30
IO... yuv422p9be             3            18
IO... yuv422p9le             3            18
IO... gbrp                   3            24
IO... gbrp9be                3            27
IO... gbrp9le                3            27
IO... gbrp10be               3            30
IO... gbrp10le               3            30
IO... gbrp16be               3            48
IO... gbrp16le               3            48
IO... yuva422p               4            24
IO... yuva444p               4            32
IO... yuva420p9be            4            22
IO... yuva420p9le            4            22
IO... yuva422p9be            4            27
IO... yuva422p9le            4            27
IO... yuva444p9be            4            36
IO... yuva444p9le            4            36
IO... yuva420p10be           4            25
IO... yuva420p10le           4            25
IO... yuva422p10be           4            30
IO... yuva422p10le           4            30
IO... yuva444p10be           4            40
IO... yuva444p10le           4            40
IO... yuva420p16be           4            40
IO... yuva420p16le           4            40
IO... yuva422p16be           4            48
IO... yuva422p16le           4            48
IO... yuva444p16be           4            64
IO... yuva444p16le           4            64
..H.. vdpau                  0             0
IO... xyz12le                3            36
IO... xyz12be                3            36
..... nv16                   3            16
..... nv20le                 3            20
..... nv20be                 3            20
IO... rgba64be               4            64
IO... rgba64le               4            64
IO... bgra64be               4            64
IO... bgra64le               4            64
IO... yvyu422                3            16
IO... ya16be                 2            32
IO... ya16le                 2            32
IO... gbrap                  4            32
IO... gbrap16be              4            64
IO... gbrap16le              4            64
..H.. qsv                    0             0
..H.. mmal                   0             0
..H.. d3d11va_vld            0             0
..H.. cuda                   0             0
IO... 0rgb                   3            24
IO... rgb0                   3            24
IO... 0bgr                   3            24
IO... bgr0                   3            24
IO... yuv420p12be            3            18
IO... yuv420p12le            3            18
IO... yuv420p14be            3            21
IO... yuv420p14le            3            21
IO... yuv422p12be            3            24
IO... yuv422p12le            3            24
IO... yuv422p14be            3            28
IO... yuv422p14le            3            28
IO... yuv444p12be            3            36
IO... yuv444p12le            3            36
IO... yuv444p14be            3            42
IO... yuv444p14le            3            42
IO... gbrp12be               3            36
IO... gbrp12le               3            36
IO... gbrp14be               3            42
IO... gbrp14le               3            42
IO... yuvj411p               3            12
I.... bayer_bggr8            3             8
I.... bayer_rggb8            3             8
I.... bayer_gbrg8            3             8
I.... bayer_grbg8            3             8
I.... bayer_bggr16le         3            16
I.... bayer_bggr16be         3            16
I.... bayer_rggb16le         3            16
I.... bayer_rggb16be         3            16
I.... bayer_gbrg16le         3            16
I.... bayer_gbrg16be         3            16
I.... bayer_grbg16le         3            16
I.... bayer_grbg16be         3            16
..H.. xvmc                   0             0
IO... yuv440p10le            3            20
IO... yuv440p10be            3            20
IO... yuv440p12le            3            24
IO... yuv440p12be            3            24
IO... ayuv64le               4            64
..... ayuv64be               4            64
..H.. videotoolbox_vld       0             0
IO... p010le                 3            15
IO... p010be                 3            15
IO... gbrap12be              4            48
IO... gbrap12le              4            48
IO... gbrap10be              4            40
IO... gbrap10le              4            40
..H.. mediacodec             0             0
IO... gray12be               1            12
IO... gray12le               1            12
IO... gray10be               1            10
IO... gray10le               1            10
IO... p016le                 3            24
IO... p016be                 3            24
..H.. d3d11                  0             0
IO... gray9be                1             9
IO... gray9le                1             9
IO... gbrpf32be              3            96
IO... gbrpf32le              3            96
IO... gbrapf32be             4            128
IO... gbrapf32le             4            128
..H.. drm_prime              0             0
..H.. opencl                 0             0
IO... gray14be               1            14
IO... gray14le               1            14
IO... grayf32be              1            32
IO... grayf32le              1            32
IO... yuva422p12be           4            36
IO... yuva422p12le           4            36
IO... yuva444p12be           4            48
IO... yuva444p12le           4            48
IO... nv24                   3            24
IO... nv42                   3            24
..H.. vulkan                 0             0
..... y210be                 3            20
I.... y210le                 3            20
IO... x2rgb10le              3            30
..... x2rgb10be              3            30

"""

import re
import warnings
from typing import Optional

from vtcff._pf_10_pixfmts_stdout_parser import pixfmt_to_spec
from vtcff._pf_15_pixfmt_subsampling import pixfmt_subsampling


def _int_if_round(f: float) -> Optional[int]:
    result = int(f)
    if abs(result - f) < 0.0000001:
        return result
    else:
        return None


def _ending(text: str) -> Optional[int]:
    m = re.search(r'(\d+)(?:le|be|$)', text)
    if m:
        return int(m.group(1))
    return None


_pix_format_to_depth = {
    # todo add important formats that are not recognized by the heuristics
    'yuv410p': 8
}


def _subsampling_factor(name: str, components: int) -> Optional[float]:
    # 4:4:4 (no alpha)   -> (4+4+4)/(4+4+4)     = 1
    # 4:2:2 (no alpha)   -> (4+2+2)/(4+4+4)     = 2/3
    # 4:4:4 (with alpha) -> (4+4+4+4)/(4+4+4+4) = 1
    # 4:2:2 (with alpha) -> (4+4+2+2)/(4+4+4+4) = 3/4

    if components not in (3, 4):
        return None
    subsampling_str = pixfmt_subsampling(name)
    if not subsampling_str:
        return None
    assert len(subsampling_str) == 3 and subsampling_str.isdigit()
    pixels_total = sum(int(c) for c in subsampling_str)
    assert 1 <= pixels_total <= 12
    pixels_max = 12
    if components == 4:
        pixels_total += 4  # assuming alpha channel always have all 4 pixels
        pixels_max += 4
    else:
        assert components == 3
    return pixels_total / pixels_max


def _guess_from_subsampling(name: str,
                            components: int,
                            bits_per_pixel: int) -> Optional[int]:
    f = _subsampling_factor(name, components)
    if f:
        return _int_if_round(bits_per_pixel / components / f)
    else:
        return None


def _guess_from_suffix(name: str, components: int, bits_per_pixel: int) -> \
        Optional[int]:
    e: Optional[int] = _ending(name)
    if e is not None:
        if e == bits_per_pixel:
            # like in rgb24, 24 means 8+8+8, 8 bit per channel
            return _int_if_round(bits_per_pixel / components)
        f = _subsampling_factor(name, components) or 1.0
        if e * components * f == bits_per_pixel:
            # yuv444p12le: 12 bits per channel
            # yuv440p10be: 10 bits per channel
            return e
    return None


def _guess_bpc(name: str, components: int, bits_per_pixel: int) \
        -> Optional[int]:
    result = (_pix_format_to_depth.get(name)
              or _guess_from_suffix(name, components, bits_per_pixel)
              or _guess_from_subsampling(name, components, bits_per_pixel))
    if result is None:
        warnings.warn(f"Color depth of {name} format is unknown.")
    return result


def pixfmt_bpc(pixfmt: str, ffmpeg_exe: str) -> Optional[int]:
    """Returns the estimated number of bits-per-color-channel after decoding
    from the specified pixel format. This value optimistically indicates the
    maximum number of color gradations in each of the channels R, G, B, A."""
    # todo test alternate path to ffmpeg_exe
    spec = pixfmt_to_spec(pixfmt, ffmpeg_exe)
    return _guess_bpc(spec.name, spec.nb_components, spec.bits_per_pixel)
