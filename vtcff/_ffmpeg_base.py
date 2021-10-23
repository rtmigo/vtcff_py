from typing import Optional, List, Iterable, Dict

from vtcff._args_subset import ArgsSubset
from vtcff._zscale import ZscaleCommand, ColorSpaces


class VtcFfmpegCommand:
    # этот класс я создаю с 2021-10 и стараюсь здесь делать всё "чисто"
    def __init__(self):
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

        # этот объект сам умеет генерировать понятные (нам) опции.
        # Но если я хочу задать команду в виде строки или списка, можно
        # поместить соответствующие параметры в следующие поля. Такие
        # параметры будут считаться более приоритетными
        self.override_general: ArgsSubset = ArgsSubset()
        self.override_audio: ArgsSubset = ArgsSubset()
        self.override_video: ArgsSubset = ArgsSubset()

    def _goc_zscale(self) -> ZscaleCommand:
        """Returns `ZscaleCommand` from the filter chain.
        If there is no such command, creates one."""
        for vf in self._filter_chain:
            if isinstance(vf, ZscaleCommand):
                return vf
        zs = ZscaleCommand()
        self._filter_chain.append(zs)
        return zs

    @property
    def dst_color_space(self) -> Optional[str]:
        return self._goc_zscale().dst_matrix

    @dst_color_space.setter
    def dst_color_space(self, val: Optional[str]):
        self._goc_zscale().dst_matrix = ColorSpaces.ffmpeg_to_zscale(val)
        self._dst_color_primaries_meta = val
        self._dst_color_trc_meta = val
        self._dst_colorspace_meta = val

    @property
    def dst_range_full(self) -> Optional[bool]:
        return self._goc_zscale().dst_range_full

    @dst_range_full.setter
    def dst_range_full(self, x: Optional[bool]):
        self._goc_zscale().dst_range_full = x
        self._dst_color_range_meta = x

    @property
    def src_range_full(self) -> Optional[bool]:
        return self._goc_zscale().src_range_full

    @src_range_full.setter
    def src_range_full(self, x: Optional[bool]):
        self._goc_zscale().src_range_full = x

    def _iter_known(self):
        # странные параметры, которые определяют "метаданные" результирующего
        # видео. В итоге оно при кодировании выглядит например как
        # (tv, bt709, progressive), а не (unknown/unknown/unknown, progressive)

        if self._filter_chain:
            yield '-vf', ','.join(str(f) for f in self._filter_chain)

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
        overrides = self._overrides_to_dict()

        for item in self._iter_known():
            if isinstance(item, str):
                yield item
            elif isinstance(item, tuple):
                k, v = item
                print(k, v)
                if k in overrides:
                    other_v = overrides[k]
                    print(f"Overriding [{k} {v}] with [{k}, {other_v}]")
                    yield k
                    yield other_v
                else:
                    yield k
                    yield v
            else:
                raise TypeError

    def __str__(self):
        return ' '.join(iter(self))
