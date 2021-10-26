from typing import Iterable
from typing import Tuple

from ._codec import Codec


class VideoCopy(Codec):
    def args(self) -> Iterable[Tuple[str, str]]:
        yield "-vcodec", "copy"
