from typing import Optional, Iterable, Tuple


class FilterBase:
    def __init__(self):
        self._pairs = dict()

    def _set_or_remove(self, key: str, val: Optional[str]):
        if val is not None:
            self._pairs[key] = val
        else:
            assert val is None
            if key in self._pairs:
                del self._pairs[key]
        assert self._pairs.get(key) == val

    @classmethod
    def _to_string(cls, name: str, kv_pairs: Iterable[Tuple[str, str]]):
        return f'{name}={":".join(k + "=" + v for (k, v) in kv_pairs)}'
