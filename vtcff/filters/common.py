from typing import NamedTuple


class Scaling(NamedTuple):
    width: int
    height: int
    downscale_only: bool