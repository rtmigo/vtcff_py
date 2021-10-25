# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from codecs import Codec
from typing import Optional, Iterable, Tuple

from ._codec_avc_preset import VcPreset
from ._common import colon_splitted_pairs


class BitrateNotSpecifiedError(Exception):
    pass


class BitrateSpecifiedForLosslessError(Exception):
    pass


class LosslessAndNearLosslessError(Exception):
    pass


class Hevc(Codec):
    def __init__(self,
                 preset: VcPreset = None,
                 lossless: bool = False,
                 near_lossless: bool = False,
                 mbps: float = None):

        self.preset: Optional[VcPreset] = preset
        self.lossless = lossless
        self.near_lossless = near_lossless
        self.mbps = mbps

    def args(self) -> Iterable[Tuple[str, str]]:

        if self.lossless and self.near_lossless:
            raise LosslessAndNearLosslessError

        yield "-vcodec", "libx265"

        params = dict()

        if self.lossless:
            params["lossless"] = "1"
            if self.mbps is not None:
                raise BitrateSpecifiedForLosslessError
        else:
            if self.near_lossless:
                # о сжатии без потерь и почти без потерь
                # https://x265.readthedocs.io/en/stable/lossless.html
                #
                # летом 2017 я заметил, что при опциях "cu-lossless=1:psy-rd=1.0"
                # стала появляться строка "x265 [warning]: --cu-lossless disabled,
                # requires --rdlevel 3 or higher". Поэтому добавил опцию rd=3

                params["cu-lossless"] = "1"
                params["psy-rd"] = "1.0"
                params["rd"] = "3"
                # params["ssim"] = "1"  # ?!

            if self.mbps is None:
                raise BitrateNotSpecifiedError
            params["bitrate"] = str(round(self.mbps * 1000))

        if self.preset is not None:
            yield "-preset", str(self.preset.value)

        if params:
            yield "-x265-params", colon_splitted_pairs(params)
