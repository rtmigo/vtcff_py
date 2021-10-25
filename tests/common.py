# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from typing import Iterable

from vtcff import FfmpegCommand


def find_item_after(items: Iterable, findme):
    it = iter(items)
    while True:
        x = next(it)
        if x == findme:
            return next(it)


def create_test_cmd(zscale=None) -> FfmpegCommand:
    if zscale is not None:
        cmd = FfmpegCommand(use_zscale=zscale)
    else:
        cmd = FfmpegCommand()
    cmd.src_file = "/tmp/path/to/src.mov"
    cmd.dst_file = "/tmp/path/to/dst.mov"
    return cmd
