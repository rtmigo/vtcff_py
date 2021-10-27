# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

import os.path
import warnings
from pathlib import Path
from typing import Optional, List, Iterable, Dict, Union, Tuple

import framefile

from vtcff._args_subset import ArgsSubset
from vtcff._codec import Codec
from vtcff._codec_audio_copy import AudioCopy
from vtcff._codec_video_copy import VideoCopy
from vtcff._common import Scale
from vtcff._filter_crop import Crop
from vtcff._filter_pad import Pad
from vtcff._filter_swscale import SwscaleFilter
from vtcff._filter_transpose import Transpose, TransposeFilter
from vtcff._filter_zscale import ZscaleFilter, ColorSpaces
from vtcff._time_span import BeginEndDuration


class VideoCodecNotSpecifiedError(Exception):
    pass


class AudioCodecNotSpecifiedError(Exception):
    pass


def arg_i(path_or_pattern: Union[str, Path]) -> List[str]:
    path_or_pattern = str(path_or_pattern)
    if '*' in path_or_pattern:
        # http://ffmpeg.org/ffmpeg.html#Video-and-Audio-file-format-conversion
        return ["-f",
                "image2",
                "-pattern_type", "glob",
                "-i", path_or_pattern]
    else:
        if os.path.isdir(path_or_pattern):
            path_or_pattern = framefile.directory_to_pattern(
                framefile.Format.percent,
                Path(path_or_pattern))
        assert isinstance(path_or_pattern, str)
        return ["-i", path_or_pattern]


def desynonimize(arg: str) -> str:
    # https://superuser.com/q/835048
    if arg in ('-vcodec', '-c:v'):
        return '-codec:v'
    if arg in ('-acodec', '-c:a'):
        return '-codec:a'
    return arg


class CustomArgs:
    def __init__(self):
        self._before_i: ArgsSubset = ArgsSubset()
        self._after_i: ArgsSubset = ArgsSubset()
        self._video: ArgsSubset = ArgsSubset()
        self._audio: ArgsSubset = ArgsSubset()

    @property
    def before_i(self) -> ArgsSubset:
        return self._before_i

    @property
    def after_i(self) -> ArgsSubset:
        return self._after_i

    @property
    def video(self) -> ArgsSubset:
        return self._video

    @property
    def audio(self) -> ArgsSubset:
        return self._audio


class FfmpegCommand:

    def __init__(self, use_zscale: bool = True):

        self._use_zscale = use_zscale

        self.ffmpeg_exe: Union[Path, str] = "ffmpeg"  # todo test
        """The ffmpeg executable file, the first argument of 
        the generated command."""

        self.src_file: Optional[Union[Path, str]] = None
        self.src_gamma: Optional[float] = None
        self.src_fps: Optional[float] = None

        self.dst_file: Optional[Union[Path, str]] = None

        # the following fields will affect the parameters that have quite
        # vague meaning. For example, when encoding, they will show
        #   yuv422p10le(tv, bt709, progressive)
        # instead
        #   yuv422p10le(tv, bt709/unknown/unknown, progressive)
        # Opinions on the web agree that this is "just meta-data",
        # and they never lead to conversion. However, and as metadata
        # they don't necessarily written anywhere as well. We will
        # pass them to ffmpeg in the hope that sometimes it will serve
        # the cause of good.
        self._dst_color_primaries_meta: Optional[str] = None
        self._dst_color_trc_meta: Optional[str] = None
        self._dst_colorspace_meta: Optional[str] = None

        # for vtcff we require video and audio codecs to be explicitly
        # specified (although for ffmpeg the are optional). But the actual
        # following filed can be set to None. Because user may want
        # to specify codecs with .custom.video, for example.
        # We will check the codecs are set at the very last stage: when
        # we get all out arguments as strings.
        self.dst_codec_video: Optional[Codec] = VideoCopy()
        self.dst_codec_audio: Optional[Codec] = AudioCopy()

        self.dst_pixfmt: Optional[str] = None

        # про -color_range
        # https://trac.ffmpeg.org/ticket/443
        self._dst_color_range_meta: Optional[bool] = None

        self._filter_chain: List = list()

        self.dst_time_range = BeginEndDuration()

        # the FfmpegCommand object can generate parameters it understands.
        # But if you want to add some exotic args, this can be done by placing
        # then in fields of the following object
        self.custom = CustomArgs()

        self.debug = False

    @property
    def override_general(self) -> ArgsSubset:
        warnings.warn("Use .custom.after_i", DeprecationWarning)  # 2021-10
        return self.custom.after_i

    @property
    def override_audio(self) -> ArgsSubset:
        warnings.warn("Use .custom.audio", DeprecationWarning)  # 2021-10
        return self.custom.audio

    @property
    def override_video(self) -> ArgsSubset:
        warnings.warn("Use .custom.video", DeprecationWarning)  # 2021-10
        return self.custom.video

    def _find_or_create_filter(self, obj_type):
        vf = self._find_filter(obj_type)
        if vf is not None:
            return vf
        result = obj_type()
        self._filter_chain.append(result)
        return result

    def _find_filter(self, obj_type):
        for vf in self._filter_chain:
            if isinstance(vf, obj_type):
                return vf
        return None

    def _replace_filter(self, obj_type, new_instance):
        for idx, item in enumerate(self._filter_chain):
            if isinstance(item, obj_type):
                self._filter_chain[idx] = new_instance
                return
        self._filter_chain.append(new_instance)

    def _remove_filter(self, obj_type):
        items_removed = 0
        for idx, item in enumerate(self._filter_chain):
            if isinstance(item, obj_type):
                del self._filter_chain[idx]
                items_removed += 1

        assert 0 <= items_removed <= 1

    def _zscale(self) -> ZscaleFilter:
        """Returns `ZscaleCommand` from the filter chain.
        If there is no such command, creates one."""
        if not self._use_zscale:
            raise Exception("_use_zscale is False")
        return self._find_or_create_filter(ZscaleFilter)

    def _swscale(self) -> SwscaleFilter:
        """Returns `ZscaleCommand` from the filter chain.
        If there is no such command, creates one."""
        if self._use_zscale:
            raise Exception("_use_zscale is True")
        return self._find_or_create_filter(SwscaleFilter)

    def _curr_scale_filter(self) -> Union[SwscaleFilter, ZscaleFilter]:
        if self._use_zscale:
            return self._zscale()
        else:
            return self._swscale()

    @property
    def use_zscale(self):
        return self._use_zscale

    @use_zscale.setter
    def use_zscale(self, x: bool):
        if x == self._use_zscale:
            return

        old_scale = self.scale
        old_src_range_full = self.src_range_full
        old_dst_range_full = self.dst_range_full
        old_src_color_space = self.src_color_space
        old_dst_color_space = self.dst_color_space

        if self._use_zscale:
            self._remove_filter(ZscaleFilter)
        else:
            self._remove_filter(SwscaleFilter)

        self._use_zscale = x
        self.scale = old_scale
        self.src_range_full = old_src_range_full
        self.dst_range_full = old_dst_range_full
        self.src_color_space = old_src_color_space
        self.dst_color_space = old_dst_color_space

    @property
    def scale(self) -> Optional[Scale]:
        if self._use_zscale:
            zs: Optional[ZscaleFilter] = self._find_filter(ZscaleFilter)
            if zs is not None:
                return zs.scaling
            return None

        else:
            sw: Optional[SwscaleFilter] = self._find_filter(
                SwscaleFilter)
            if sw is not None and sw.width is not None:
                assert sw.height is not None
                return Scale(sw.width, sw.height, sw.downscale_only)
            return None

    @scale.setter
    def scale(self, s: Optional[Scale]):

        if self._use_zscale:
            zs: ZscaleFilter = self._find_or_create_filter(ZscaleFilter)
            zs.scaling = s
        else:
            sw: SwscaleFilter = self._find_or_create_filter(SwscaleFilter)
            if s is not None:
                sw.width, sw.height = s.width, s.height
                sw.downscale_only = s.downscale_only
            else:
                sw.width = None
                sw.height = None
                sw.downscale_only = False

    @property
    def transpose(self) -> Optional[Transpose]:
        f: Optional[TransposeFilter] = self._find_filter(TransposeFilter)
        if f is None:
            return None
        else:
            return f.kind

    @transpose.setter
    def transpose(self, x: Transpose):
        f: TransposeFilter = self._find_or_create_filter(TransposeFilter)
        f.kind = x

    @property
    def crop(self) -> Optional[Crop]:
        return self._find_filter(Crop)

    @crop.setter
    def crop(self, x: Crop):
        self._replace_filter(Crop, x)

    @property
    def _pad(self) -> Optional[Pad]:
        """Marked private because not tested."""
        # todo test
        return self._find_filter(Pad)

    @_pad.setter
    def _pad(self, x: Pad):
        """Marked private because not tested."""
        # todo test
        self._replace_filter(Pad, x)

    @property
    def src_color_space(self) -> Optional[str]:
        if self._use_zscale:
            # todo test
            return ColorSpaces.zscale_to_ffmpeg(self._zscale().src_matrix)
        else:
            # todo test
            return self._swscale().src_matrix

    @src_color_space.setter
    def src_color_space(self, val: Optional[str]):
        if self._use_zscale:
            self._zscale().src_matrix = ColorSpaces.ffmpeg_to_zscale(val)
        else:
            # todo test
            self._swscale().src_matrix = val

    @property
    def dst_color_space(self) -> Optional[str]:
        if self._use_zscale:
            # todo test
            return ColorSpaces.zscale_to_ffmpeg(self._zscale().dst_matrix)
        else:
            # todo test
            return self._swscale().dst_matrix

    @dst_color_space.setter
    def dst_color_space(self, val: Optional[str]):
        if self._use_zscale:
            self._zscale().dst_matrix = ColorSpaces.ffmpeg_to_zscale(val)
        else:
            self._swscale().dst_matrix = val

        self._dst_color_primaries_meta = val
        self._dst_color_trc_meta = val
        self._dst_colorspace_meta = val

    @property
    def dst_range_full(self) -> Optional[bool]:
        return self._curr_scale_filter().dst_range_full

    @dst_range_full.setter
    def dst_range_full(self, x: Optional[bool]):
        self._curr_scale_filter().dst_range_full = x
        self._dst_color_range_meta = x

    @property
    def src_range_full(self) -> Optional[bool]:
        return self._curr_scale_filter().src_range_full

    @src_range_full.setter
    def src_range_full(self, x: Optional[bool]):
        self._curr_scale_filter().src_range_full = x

    def _iter_known_before_i(self) -> Iterable[Union[str, Tuple[str, str]]]:
        yield str(self.ffmpeg_exe)

        # для файлов EXR стоит указывать что-то вроде '-gamma 2.2', причем
        # еще до аргумента -i
        if self.src_gamma:
            yield "-gamma", str(self.src_gamma)

        if self.src_fps:
            # в случае сборки видео отдельных файлов-кадров, важно
            # указать частоту кадров _перед_ аргументом -i.
            #
            # Примерно так:
            #   ffmpeg -r 30 -f image2 -pattern_type glob -i '/path/*.png'
            #   ffmpeg -r 30 -i '/path/%04d.png'
            #
            # Параметр -r, указанный позже, будет уже касаться более
            # поздних стадий обработки видео. При этом ffmpeg будет
            # читать исходные файлы, предполагая, что каждый из них
            # имеет длительность 1/25 сек (т.е. 25 fps). Результирующий
            # файл может иметь обманчивую частоту кадров 30. Но
            # не будет прямого соответствия между исходными кадрами
            # и сохраненными. Например, из 300 файлов-кадров получится
            # 360-кадровое 12-секундное видео 30 fps. Так было бы при
            # конвертировании 25 fps в 30 fps.

            # TL;DR: -framerate is for image sequences
            #
            # -framerate is an input per-file option. It is meant for input
            # formats which don't have a framerate or PTS defined, image
            # sequences being an example (https://stackoverflow.com/a/51224132)
            yield '-framerate', str(self.src_fps)

            # TL;DR: -r is for video files, it changes the rate
            #
            # -r can be either an input or output option. As an input option,
            # it retimes input frames at that rate. As an output option,
            # it will duplicate or drop frames to achieve the given rate
            # (https://stackoverflow.com/a/51224132)
            yield '-r', str(self.src_fps)

    def _iter_known_all_after_i(self) -> Iterable[
        Union[str, Tuple[str, Optional[str]]]]:
        if self.dst_time_range.begin:
            yield "-ss", str(self.dst_time_range.begin)
        if self.dst_time_range.duration is not None:
            yield "-t", str(self.dst_time_range.duration)
        if self._filter_chain:
            vf_str = ','.join(str(f) for f in self._filter_chain)
            if vf_str:
                yield '-vf', vf_str

        if self.dst_codec_video is not None:
            for pair in self.dst_codec_video.args():
                yield pair

        if self.dst_pixfmt:
            yield '-pix_fmt', self.dst_pixfmt

        # странные параметры, которые определяют "метаданные" результирующего
        # видео. В итоге оно при кодировании выглядит например как
        # (tv, bt709, progressive), а не (unknown/unknown/unknown, progressive)

        if self._dst_colorspace_meta is not None:
            yield '-colorspace', self._dst_colorspace_meta
        if self._dst_color_primaries_meta is not None:
            yield '-color_primaries', self._dst_color_primaries_meta
        if self._dst_color_trc_meta is not None:
            yield '-color_trc', self._dst_color_trc_meta

        if self._dst_color_range_meta is not None:
            # https://trac.ffmpeg.org/ticket/443
            # "0" auto, "1" 16-235, "2" 0-255
            yield '-color_range', '2' if self._dst_color_range_meta else '1'

        yield '-movflags', '+write_colr'
        yield ('-sws_flags',
               'spline+accurate_rnd+full_chroma_int+full_chroma_inp')

        if self.dst_codec_audio is not None:
            for pair in self.dst_codec_audio.args():
                yield pair

        if self.debug:
            yield '-loglevel', 'verbose'

        # последним в списке аргументов должно идти имя целевого файла.
        # Но здесь мы его не возвращаем - метод __iter__ добавит перед именем
        # файла еще что-то - и потом сам допишет имя

    def _combine_overrides(self, src: Iterable[Dict[str, Optional[str]]]) \
            -> Dict[str, Optional[str]]:
        overrides: Dict[str, Optional[str]] = dict()
        for ov in src:
            for k, v in ov.items():
                # todo test overriding overrides
                if k in overrides:
                    print(f"Overriding [{k} {overrides[k]}] with [{k}, {v}]")
                overrides[k] = v
        return overrides

    def _iter_replacing_overrides(
            self,
            args_or_pairs: Iterable[Union[str, Tuple[str, Optional[str]]]],
            overrides: Dict[str, Optional[str]]) \
            -> Iterable[str]:

        returned_keys = set()

        k: str
        v: Optional[str]

        for item in args_or_pairs:
            if isinstance(item, str):
                yield item
            elif isinstance(item, tuple):
                k, v = item
                if k in overrides:
                    other_v = overrides[k]
                    print(f"Overriding [{k} {v}] with [{k}, {other_v}]")
                    yield k
                    if other_v is not None:
                        yield other_v
                else:
                    yield k
                    if v is not None:
                        yield v
                returned_keys.add(k)
            else:
                raise TypeError

        # до сих пор мы генерировали последовательность известных объекту
        # аргументов в привычном нам порядке. Некоторые аргументы могли быть
        # подменены на значения из словаря overrides. Но возможно в словаре
        # overrides есть и другие аргументы, до сих пор не упомянутые.
        # Возвращаем теперь их
        for k, v in overrides.items():
            if k not in returned_keys:
                yield k
                if v is not None:
                    yield v

    def _iter_almost_final(self) -> Iterable[str]:
        """Возвращает аргументы к команде ffmpeg списком."""

        for x in self._iter_replacing_overrides(
                self._iter_known_before_i(),
                dict(self.custom.before_i.pairs())):
            yield x

        if self.src_file:  # todo это не должно быть опциональным
            for arg in arg_i(self.src_file):
                yield arg

        combined_overrides_after_i = self._combine_overrides([
            dict(self.custom.after_i.pairs()),
            dict(self.custom.video.pairs()),
            dict(self.custom.audio.pairs()),
        ])

        for x in self._iter_replacing_overrides(
                self._iter_known_all_after_i(),
                combined_overrides_after_i):
            yield x

        # последним в списке аргументов идет имя целевого файла
        if self.dst_file is None:
            raise ValueError("Output file not specified")
        yield str(self.dst_file)

    def __iter__(self) -> Iterable[str]:
        args = list(desynonimize(arg) for arg in self._iter_almost_final())

        if not any(s in args for s in ("-codec:v", "-vn")):
            raise VideoCodecNotSpecifiedError(args)

        # The -vn / -an / -sn / -dn options can be used to skip inclusion
        # of video, audio, subtitle and data streams respectively
        if not any(s in args for s in ("-codec:a", "-an")):
            raise AudioCodecNotSpecifiedError
        return iter(args)

    def __str__(self):
        return ' '.join(iter(self))
