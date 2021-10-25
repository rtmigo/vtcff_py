# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from codecs import Codec
from typing import Optional, Iterable, Tuple

from ._codec_avc_preset import VcPreset
from ._common import colon_splitted_pairs


class Hevc(Codec):
    def __init__(self, preset: VcPreset = None, lossless: bool = False):
        self.preset: Optional[VcPreset] = preset
        self.lossless = lossless

    def args(self) -> Iterable[Tuple[str, str]]:
        yield "-vcodec", "libx265"

        params = dict()
        if self.lossless:
            params["lossless"] = "1"

        if self.preset is not None:
            yield "-preset", str(self.preset.value)

        if params:
            yield "-x265-params", colon_splitted_pairs(params)
