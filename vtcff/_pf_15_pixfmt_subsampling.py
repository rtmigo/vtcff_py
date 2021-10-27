import re
from typing import Optional


def _three_digits(text) -> Optional[str]:
    """True if `text` contains something like aXXXb, where XXX are digits
    and a, b - are not."""
    m = re.search(r'(?<!\d)([01234]{3})(?!\d)', text)
    if m:
        return str(m.group(1))
    else:
        return None


def pixfmt_subsampling(pixfmt: str) -> Optional[str]:
    td = _three_digits(pixfmt)
    if td:
        return td
    if any(s in pixfmt for s in ('rgb', 'bgr', 'gbr')):
        return '444'
    return None


