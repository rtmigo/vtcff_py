# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from typing import NamedTuple, Union, Dict, Iterable, Tuple


class Scale(NamedTuple):
    width: int
    height: int
    downscale_only: bool = False


def colon_splitted_pairs(items: Union[Dict[str, str], Iterable[Tuple[str,str]]]) -> str:
    if isinstance(items, dict):
        items = items.items()
    return ':'.join(f"{k}={v}" for (k, v) in items)