# (c) 2021 Artёm IG <github.com/rtmigo>

from typing import Optional, List, Iterable, Dict, NamedTuple

from vtcff._args_subset import ArgsSubset
from vtcff._time_span import BeginEndDuration
from vtcff._zscale import ZscaleCommand, ColorSpaces
from vtcff.filters._swscale_scale import SwscaleScaleFilter
from vtcff.filters._transpose import Transpose, TransposeFilter


class Scaling(NamedTuple):
    width: int
    height: int
    downscale_only: bool


class VtcFfmpegCommand:
    def __init__(self, use_zscale: bool = False):

        self._use_zscale = use_zscale

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

        self.write_time_range = BeginEndDuration()

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

    def _zscale(self) -> ZscaleCommand:
        """Returns `ZscaleCommand` from the filter chain.
        If there is no such command, creates one."""
        if not self._use_zscale:
            raise Exception("_use_zscale is False")
        return self._find_or_create_filter(ZscaleCommand)

    @property
    def scaling(self) -> Optional[Scaling]:
        if self._use_zscale:
            raise Exception("Not implemented for zscale")

        f: Optional[SwscaleScaleFilter] = self._find_filter(SwscaleScaleFilter)
        if f is not None:
            return Scaling(f.wh[0], f.wh[1], f.downscale_only)
        return None

    @scaling.setter
    def scaling(self, s: Scaling):
        if self._use_zscale:
            raise Exception("Not implemented for zscale")
        f: SwscaleScaleFilter = self._find_or_create_filter(SwscaleScaleFilter)
        f.wh = s.width, s.height
        f.downscale_only = s.downscale_only

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
        # странные параметры, которые определяют "метаданные" результирующего
        # видео. В итоге оно при кодировании выглядит например как
        # (tv, bt709, progressive), а не (unknown/unknown/unknown, progressive)

        if self.write_time_range.begin:
            yield "-ss", str(self.write_time_range.begin)
        if self.write_time_range.duration is not None:
            yield "-t", str(self.write_time_range.duration)

        if self._filter_chain:
            vf_str = ','.join(str(f) for f in self._filter_chain)
            if vf_str:
                yield '-vf', vf_str

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
        yield '-sws_flags', 'spline+accurate_rnd+full_chroma_int+full_chroma_inp'

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

    def __str__(self):
        return ' '.join(iter(self))
