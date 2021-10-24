from typing import Iterable, Tuple


class Codec:
    def __iter__(self) -> Iterable[Tuple[str, str]]:
        raise NotImplementedError
