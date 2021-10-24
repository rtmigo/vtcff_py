from enum import unique, IntEnum
from typing import Optional, Tuple, Iterable

from ._codec import Codec


@unique
class ProresProfile(IntEnum):
    proxy = 0
    """ProRes 422 Proxy"""

    lt = 1
    """ProRes 422 LT"""

    normal = 2
    """ProRes 422"""

    hq = 3
    """ProRes 422 HQ"""

    four = 4
    """ProRes 4444"""

    xq = 5
    """ProRes 4444 XQ"""


class Prores(Codec):
    def __init__(self,
                 profile: ProresProfile = ProresProfile.normal,
                 qscale: Optional[int] = None,
                 spoof_vendor: bool = False):
        self.profile: ProresProfile = profile
        self.qscale: Optional[int] = qscale
        self.spoof_vendor: bool = spoof_vendor

    def __iter__(self) -> Iterable[Tuple[str, str]]:
        yield '-vcodec', 'prores_ks'
        if self.spoof_vendor:
            yield '-vendor', 'apl0'
        if self.qscale is not None:
            yield '-q:v', str(self.qscale)
        if self.profile is not None:
            yield '-profile:v', str(self.profile.value)
