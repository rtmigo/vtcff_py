from codecs import Codec
from typing import Optional, Iterable, Tuple

from vtcff import VcPreset


class Hevc(Codec):
    def __init__(self, preset: VcPreset = None):
        self.preset: Optional[VcPreset] = preset

    def __iter__(self) -> Iterable[Tuple[str, str]]:
        yield "-vcodec", "libx265"

        if self.preset is not None:
            yield "-preset", str(self.preset.value)
