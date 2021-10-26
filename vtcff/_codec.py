# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from typing import Iterable, Tuple, Optional


class Codec:
    def args(self) -> Iterable[Tuple[str, Optional[str]]]:
        raise NotImplementedError


class VideoCodec(Codec):
    pass


class AudioCodec(Codec):
    pass
