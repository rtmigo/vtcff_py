# (c) 2021 Artёm IG <github.com/rtmigo>

from pathlib import Path
from typing import Optional, List, Iterable, Dict, Union

from vtcff._args_subset import ArgsSubset
from vtcff._encspeed import Speed
from vtcff._time_span import BeginEndDuration
from vtcff.filters._cropping import Crop
from vtcff.filters._padding import Pad
from vtcff.filters._swscale_scale import SwscaleScaleFilter
from vtcff.filters._transpose import Transpose, TransposeFilter
from vtcff.filters._zscale import ZscaleCommand, ColorSpaces
from vtcff.filters.common import Scale


def arg_i(path_or_pattern: str) -> List[str]:
    if '*' in path_or_pattern:
        # http://ffmpeg.org/ffmpeg.html#Video-and-Audio-file-format-conversion
        return ["-f",
                "image2",
                "-pattern_type", "glob",
                # чтобы передать аргумент со звездочкой внутрь ffmpeg
                # (а не раскрыть эту звездочку на уровне среды),
                # берем аргумент в кавычки. Но если я стану запускать ffmpeg
                # при помощи Popen, кавычки нужно будет убрать
                "-i", path_or_pattern]
    else:
        return ["-i", path_or_pattern]


class FfmpegCommand:
    def __init__(self, use_zscale: bool = False):

        self._use_zscale = use_zscale

        self.src_file: Optional[Union[Path, str]] = None
        self.src_gamma: Optional[float] = None
        self.src_fps: Optional[float] = None

        self.dst_file: Optional[Union[Path, str]] = None

        self.speed: Optional[Speed] = None

        # следующие поля будут влиять на параметры, которые имеют довольно
        # туманное значение. Например, чтобы при кодировании видеть
        #   yuv422p10le(tv, bt709, progressive)
        # а не
        #   yuv422p10le(tv, bt709/unknown/unknown, progressive)
        # Может ли задание этих параметров приводить к конвертированию -
        # большой вопрос. Но если я сам при помощи zscale делаю себе bt709,
        # то задаю и эти параметры
        self._dst_color_primaries_meta: Optional[str] = None
        self._dst_color_trc_meta: Optional[str] = None
        self._dst_colorspace_meta: Optional[str] = None

        # про -color_range
        # https://trac.ffmpeg.org/ticket/443
        self._dst_color_range_meta: Optional[bool] = None

        self._filter_chain: List = list()

        self.dst_time_range = BeginEndDuration()

        # этот объект сам умеет генерировать понятные (нам) опции.
        # Но если я хочу задать команду в виде строки или списка, можно
        # поместить соответствующие параметры в следующие поля. Эти параметры
        # считаются более приоритетными и заменят сгенерированные (при
        # условии, что имеют формат '-key value')
        self.override_general: ArgsSubset = ArgsSubset()
        self.override_audio: ArgsSubset = ArgsSubset()
        self.override_video: ArgsSubset = ArgsSubset()

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

    def _zscale(self) -> ZscaleCommand:
        """Returns `ZscaleCommand` from the filter chain.
        If there is no such command, creates one."""
        if not self._use_zscale:
            raise Exception("_use_zscale is False")
        return self._find_or_create_filter(ZscaleCommand)

    @property
    def scale(self) -> Optional[Scale]:
        if self._use_zscale:
            zs: Optional[ZscaleCommand] = self._find_filter(ZscaleCommand)
            if zs is not None:
                return zs.scaling
            return None

        else:
            sw: Optional[SwscaleScaleFilter] = self._find_filter(
                SwscaleScaleFilter)
            if sw is not None:
                return Scale(sw.wh[0], sw.wh[1], sw.downscale_only)
            return None

    @scale.setter
    def scale(self, s: Scale):
        if self._use_zscale:
            zs: ZscaleCommand = self._find_or_create_filter(ZscaleCommand)
            zs.scaling = s
        else:
            sw: SwscaleScaleFilter = self._find_or_create_filter(
                SwscaleScaleFilter)
            sw.wh = s.width, s.height
            sw.downscale_only = s.downscale_only

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
    def dst_color_space(self) -> Optional[str]:
        return self._zscale().dst_matrix

    @dst_color_space.setter
    def dst_color_space(self, val: Optional[str]):
        self._zscale().dst_matrix = ColorSpaces.ffmpeg_to_zscale(val)
        self._dst_color_primaries_meta = val
        self._dst_color_trc_meta = val
        self._dst_colorspace_meta = val

    @property
    def dst_range_full(self) -> Optional[bool]:
        return self._zscale().dst_range_full

    @dst_range_full.setter
    def dst_range_full(self, x: Optional[bool]):
        self._zscale().dst_range_full = x
        self._dst_color_range_meta = x

    @property
    def src_range_full(self) -> Optional[bool]:
        return self._zscale().src_range_full

    @src_range_full.setter
    def src_range_full(self, x: Optional[bool]):
        self._zscale().src_range_full = x

    def _iter_known(self):
        yield "ffmpeg"

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

        if self.src_file:  # todo это не должно быть опциональным
            for arg in arg_i(self.src_file):
                yield arg

        if self.dst_time_range.begin:
            yield "-ss", str(self.dst_time_range.begin)
        if self.dst_time_range.duration is not None:
            yield "-t", str(self.dst_time_range.duration)

        if self._filter_chain:
            vf_str = ','.join(str(f) for f in self._filter_chain)
            if vf_str:
                yield '-vf', vf_str

        if self.speed is not None:
            yield '-preset', self.speed.value

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

        # последним в списке аргументов должно идти имя целевого файла.
        # Но здесь мы его не возвращаем - метод __iter__ добавит перед именем
        # файла еще что-то - и потом сам допишет имя

    def _overrides_to_dict(self) -> Dict[str, Optional[str]]:
        overrides: Dict[str, Optional[str]] = dict()
        for ov in [self.override_general,
                   self.override_video,
                   self.override_audio]:
            for k, v in ov.pairs():
                # todo test overriding overrides
                if k in overrides:
                    print(f"Overriding [{k} {overrides[k]}] with [{k}, {v}]")
                overrides[k] = v
        return overrides

    def __iter__(self) -> Iterable[str]:
        """Возвращает аргументы к команде ffmpeg списком."""
        overrides = self._overrides_to_dict()

        returned_keys = set()

        for item in self._iter_known():
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

        # последним в списке аргументов идет имя целевого файла
        if self.dst_file is None:
            raise ValueError("Output file not specified")
        yield str(self.dst_file)

    def __str__(self):
        return ' '.join(iter(self))
