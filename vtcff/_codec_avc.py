# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from codecs import Codec
from typing import Optional, Iterable, Tuple

from ._codec_avc_preset import VcPreset


class Avc(Codec):
    def __init__(self, preset: VcPreset = None):
        self.preset: Optional[VcPreset] = preset

    def __iter__(self) -> Iterable[Tuple[str, str]]:
        yield "-vcodec", "libx264"

        if self.preset is not None:
            yield "-preset", str(self.preset.value)
