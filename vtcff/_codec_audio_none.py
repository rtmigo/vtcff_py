# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from typing import Iterable, Optional
from typing import Tuple

from ._codec import AudioCodec


class NoAudio(AudioCodec):
    def args(self) -> Iterable[Tuple[str, Optional[str]]]:
        yield "-an", None
