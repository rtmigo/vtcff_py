# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from typing import Optional


class BeginEndDuration:
    def __init__(self):
        self.begin: float = 0
        self.duration: Optional[float] = None

    @property
    def end(self):
        if self.duration is None:
            return None
        else:
            return self.begin + self.duration

    @end.setter
    def end(self, x: Optional[float]):
        if x is None:
            self.duration = None
        else:
            self.duration = x - self.begin

