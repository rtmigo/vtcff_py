# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from enum import IntEnum, unique


@unique
class Transpose(IntEnum):
    # https://stackoverflow.com/questions/3937387/rotating-videos-with-ffmpeg
    CounterClockwiseVflip = 0
    Clockwise = 1
    CounterClockwise = 2
    ClockwiseVflip = 3


class TransposeFilter:
    def __init__(self):
        self.kind = Transpose.Clockwise

    def __str__(self):
        return f"transpose={self.kind.value}"
