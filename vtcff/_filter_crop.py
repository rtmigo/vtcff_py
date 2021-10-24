# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from typing import NamedTuple


class Crop(NamedTuple):
    left: int = 0
    top: int = 0
    width: int = 0
    height: int = 0

    def __str__(self):
        # def cropRect(self, rectPosX, rectPosY, rectWidth, rectHeight):
        #     cropFilter = "crop=%s:%s:%s:%s" % (
        #         rectWidth, rectHeight, rectPosX, rectPosY)
        return "crop=%s:%s:%s:%s" \
               % (self.width, self.height, self.left, self.top)
