# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from typing import Optional, Iterable, Tuple

from ._codec import VideoCodec
from ._codec_avc_preset import VcPreset
from ._common import colon_splitted_pairs


class HevcBitrateNotSpecifiedError(Exception):
    pass


class HevcBitrateSpecifiedForLosslessError(Exception):
    pass


class HevcLosslessAndNearLosslessError(Exception):
    pass


class Hevc(VideoCodec):
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
            raise HevcLosslessAndNearLosslessError

        yield "-codec:v", "libx265"

        params = dict()

        if self.lossless:
            params["lossless"] = "1"
            # we should NOT specify bitrate for lossless encoding
            if self.mbps is not None:
                raise HevcBitrateSpecifiedForLosslessError
        else:
            if self.near_lossless:
                # https://x265.readthedocs.io/en/stable/lossless.html

                params["cu-lossless"] = "1"
                params["psy-rd"] = "1.0"

                # without the following param we may get
                # "x265 [warning]: --cu-lossless disabled,
                # requires --rdlevel 3 or higher"
                params["rd"] = "3"
                # params["ssim"] = "1"  # ?!

            if self.mbps is None:
                raise HevcBitrateNotSpecifiedError
            params["bitrate"] = str(round(self.mbps * 1000))

        p = self.preset
        if p is None:
            if self.lossless:
                # we are not losing any quality here,
                # we want better-than-prores result fast
                p = VcPreset.N1_ULTRAFAST
            elif self.near_lossless:
                # safest bet is highest quality
                p = VcPreset.N10_PLACEBO

        if p is not None:
            yield "-preset", str(p.value)

        if params:
            yield "-x265-params", colon_splitted_pairs(params)
