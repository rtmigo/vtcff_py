# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from enum import IntEnum, unique


@unique
class Transpose(IntEnum):
    # https://stackoverflow.com/questions/3937387/rotating-videos-with-ffmpeg
    COUNTER_CLOCKWISE_VFLIP = 0
    CLOCKWISE = 1
    COUNTER_CLOCKWISE = 2
    CLOCKWISE_VFLIP = 3


class TransposeFilter:
    def __init__(self):
        self.kind = Transpose.CLOCKWISE

    def __str__(self):
        return f"transpose={self.kind.value}"
