# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from typing import Iterable, Tuple


class Codec:
    def args(self) -> Iterable[Tuple[str, str]]:
        raise NotImplementedError
