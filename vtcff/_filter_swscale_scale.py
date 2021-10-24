# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

class SwscaleScaleFilter:
    def __init__(self):
        self.wh = (-1, -1)
        self.downscale_only = False

    def __str__(self):
        pfx = "scale="
        if self.downscale_only:
            w, h = self.wh
            return pfx + ':'.join(
                [f"'min(iw,{w})'" if w > 0 else str(w),
                 f"'min(ih,{h})'" if h > 0 else str(h)])
        else:
            return f'{pfx}{self.wh[0]}:{self.wh[1]}'  # -1:'min(ih,720)
