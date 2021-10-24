# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from __future__ import annotations

from enum import Enum, unique
from typing import List


@unique
class VcPreset(Enum):
    # https://trac.ffmpeg.org/wiki/Encode/H.264
    # https://trac.ffmpeg.org/wiki/Encode/H.265

    N1_ULTRAFAST = "ultrafast"
    N2_SUPERFAST = "superfast"
    N3_VERYFAST = "veryfast"
    N4_FASTER = "faster"
    N5_FAST = "fast"
    N6_MEDIUM = "medium"
    N7_SLOW = "slow"
    N8_SLOWER = "slower"
    N9_VERYSLOW = "veryslow"
    N10_PLACEBO = "placebo"

    @classmethod
    def faster(cls, speed: VcPreset) -> VcPreset:
        arr: List[VcPreset] = list(cls)
        idx = arr.index(speed)
        if idx < 0:
            raise ValueError
        if idx == 0:
            raise IndexError
        return arr[idx - 1]
