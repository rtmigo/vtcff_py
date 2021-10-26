# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from typing import Iterable

from vtcff import FfmpegCommand, AudioCopy, VideoCopy


def find_item_after(items: Iterable, findme):
    it = iter(items)
    while True:
        x = next(it)
        if x == findme:
            return next(it)


def unique_item_after(items: Iterable, findme):
    it = iter(items)
    results = []
    while True:
        try:
            x = next(it)
            if x == findme:
                results.append(next(it))
        except StopIteration:
            break
    if len(results) != 1:
        raise ValueError(results)
    return results[0]


def create_test_cmd(zscale=None) -> FfmpegCommand:
    if zscale is not None:
        cmd = FfmpegCommand(use_zscale=zscale)
    else:
        cmd = FfmpegCommand()
    cmd.src_file = "/tmp/path/to/src.mov"
    cmd.dst_file = "/tmp/path/to/dst.mov"
    # if codecs:
    #     cmd.dst_codec_video = VideoCopy()
    #     cmd.dst_codec_audio = AudioCopy()
    return cmd


