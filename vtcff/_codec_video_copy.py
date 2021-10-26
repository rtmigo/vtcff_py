# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from typing import Iterable
from typing import Tuple

from ._codec import VideoCodec


class VideoCopy(VideoCodec):
    def args(self) -> Iterable[Tuple[str, str]]:
        yield "-codec:v", "copy"
