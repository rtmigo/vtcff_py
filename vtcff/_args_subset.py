# (c) 2021 Artёm IG <github.com/rtmigo>

import shlex
from typing import List, Iterable, Tuple, Optional


class ArgsSubset:
    def __init__(self):
        self.list: List[str] = list()

    @property
    def string(self) -> str:
        return shlex.join(self.list)

    @string.setter
    def string(self, value: str):
        self.list = shlex.split(value)

    def pairs(self) -> Iterable[Tuple[str, Optional[str]]]:

        def is_key(s):
            return s.startswith('-')

        prev_key = None
        for arg in self.list:
            if prev_key is None:
                if is_key(arg):
                    prev_key = arg
                    continue
                else:
                    raise ValueError(arg)

            else:
                assert prev_key is not None
                if is_key(arg):
                    yield prev_key, None
                    prev_key = arg
                else:
                    assert prev_key is not None and not is_key(arg)
                    yield prev_key, arg
                    prev_key = None

        if prev_key is not None:
            yield prev_key, None


