# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from typing import NamedTuple


class Scale(NamedTuple):
    width: int
    height: int
    downscale_only: bool = False
