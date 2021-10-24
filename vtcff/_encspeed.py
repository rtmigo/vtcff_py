from __future__ import annotations

from enum import Enum, unique


@unique
class Speed(Enum):
    # https://trac.ffmpeg.org/wiki/Encode/H.264
    # https://trac.ffmpeg.org/wiki/Encode/H.265

    n1_ultrafast = "ultrafast"
    n2_superfast = "superfast"
    n3_veryfast = "veryfast"
    n4_faster = "faster"
    n5_fast = "fast"
    n6_medium = "medium"
    n7_slow = "slow"
    n8_slower = "slower"
    n9_veryslow = "veryslow"
    n10_placebo = "placebo"

    @classmethod
    def faster(cls, speed: Speed) -> Speed:
        arr = list(cls)
        idx = arr.index(speed)
        if idx < 0:
            raise ValueError
        if idx == 0:
            raise IndexError
        return arr[idx - 1]
