# SPDX-FileCopyrightText: (c) 2016-2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT


from ._command import FfmpegCommand, Scale
from ._filter_pad import Pad


class LetterboxSizes:
    def __init__(self,
                 src_width: int, src_height: int,
                 dst_width: int, dst_height: int):

        src_aspect = src_width / src_height
        dst_aspect = dst_width / dst_height

        needSourceWidth = int(round(dst_aspect * src_height))
        # если бы ширина исходника была равна этому значению,
        # а высота неизменна, то в обоих файлах соотношение сторон было
        # бы одинаковым

        self.pad_left = 0
        self.pad_right = 0
        self.pad_top = 0
        self.pad_bottom = 0

        if needSourceWidth != src_width:
            # придется добавлять полосы
            if src_aspect > dst_aspect:
                # исходник шире, чем результат
                # нужно добавить к исходнику полосы сверху и снизу
                need_source_height = src_width / dst_aspect
                assert need_source_height > src_height
                padding_total = need_source_height - src_height
                padding_half = int(round(padding_total / 2))
                self.pad_top = padding_half
                self.pad_bottom = int(round(padding_total - padding_half))
            else:
                # исходник уже, чем результат
                # нужно добавить к исходнику полосы слева и справа
                assert needSourceWidth > src_width
                padding_total = needSourceWidth - src_width
                padding_half = int(round(padding_total / 2))
                self.pad_left = padding_half
                self.pad_right = padding_total - padding_half


def pad_lrtb_to_lrwh(pad_left=0, pad_right=0, pad_top=0, pad_bottom=0):
    # добавляет черные полоски по бокам видео

    if pad_left < 0:
        raise Exception("padLeft must not be negative.")
    if pad_right < 0:
        raise Exception("padRight must not be negative.")
    if pad_top < 0:
        raise Exception("padTop must not be negative.")
    if pad_bottom < 0:
        raise Exception("padBottom must not be negative.")

    width = "iw"
    height = "ih"
    x = 0
    y = 0

    if any(v > 0 for v in [pad_left, pad_right, pad_top, pad_bottom]):
        width = "iw+%d" % int(pad_left + pad_right)
        height = "ih+%d" % int(pad_top + pad_bottom)
        x = int(pad_left)
        y = int(pad_top)

    return x, y, width, height


def _letterbox(cmd: FfmpegCommand,
               src_width: int, src_height: int,
               dst_width: int, dst_height: int):
    """Marked private because not tested."""
    # todo test
    sizes = LetterboxSizes(src_width=src_width, src_height=src_height,
                           dst_width=dst_width, dst_height=dst_height)
    l, t, w, h = pad_lrtb_to_lrwh(pad_left=sizes.pad_left,
                                  pad_right=sizes.pad_right,
                                  pad_top=sizes.pad_top,
                                  pad_bottom=sizes.pad_bottom)
    cmd._pad = Pad(left=l, top=t, width=w, height=h)
    cmd.scale = Scale(-2, dst_height)
