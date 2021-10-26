# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from typing import Optional, Iterable, Tuple

from ._codec import VideoCodec
from ._codec_avc_preset import VcPreset


class Avc(VideoCodec):
    def __init__(self, preset: VcPreset = None):
        self.preset: Optional[VcPreset] = preset

    def args(self) -> Iterable[Tuple[str, str]]:
        yield "-codec:v", "libx264"

        if self.preset is not None:
            yield "-preset", str(self.preset.value)
