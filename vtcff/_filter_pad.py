# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from typing import NamedTuple, Union


class Pad(NamedTuple):
    # значениями полей может быть размер или что-то вроде "iw+10"
    left: Union[int, str] = 0
    top: Union[int, str] = 0
    width: Union[int, str] = 0
    height: Union[int, str] = 0
    color: str = 'black'

    def __str__(self):
        return "pad=width=%s:height=%s:x=%s:y=%s:color=%s" \
               % (self.width, self.height, self.left, self.top, self.color)
