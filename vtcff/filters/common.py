from typing import NamedTuple


class Scale(NamedTuple):
    width: int
    height: int
    downscale_only: bool = False