# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from typing import NamedTuple, Union, Dict, Iterable, Tuple


class Scale(NamedTuple):
    width: int
    height: int
    downscale_only: bool = False


def colon_splitted_pairs(
        items: Union[Dict[str, str], Iterable[Tuple[str, str]]]) -> str:
    if isinstance(items, dict):
        items = items.items()
    return ':'.join(f"{k}={v}" for (k, v) in items)


def frame_dimension_spec(iw_or_ih: str, value: int,
                         downscale_only: bool) -> str:
    assert iw_or_ih in ('iw', 'ih')
    if not downscale_only:
        return str(value)

    # итак, мы собираемся только уменьшать. Значит, хотим что-то вроде
    #   'min(iw,1920)':'min(ih,1080)' (если оба размера заданы)
    # или
    #   -2:'min(ih,1080)' (если один задан, а второй должен быть пропорционален)

    if value >= 0:
        return f"'min({iw_or_ih},{value})'"
    else:
        assert value < 0
        return str(value)
