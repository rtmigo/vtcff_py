from typing import Iterable, Optional
from typing import Tuple

from ._codec import Codec


class NoAudio(Codec):
    def args(self) -> Iterable[Tuple[str, Optional[str]]]:
        yield "-an", None
