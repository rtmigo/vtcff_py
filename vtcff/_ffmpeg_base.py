from typing import Optional

from vtcff._zscale import ZscaleCommand, ColorSpaces


class VtcFfmpegCommand:
    # этот класс я создаю с 2021-10 и стараюсь здесь делать всё "чисто"
    def __init__(self):
        self._zscale = ZscaleCommand()

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

    @property
    def dst_color_space(self) -> Optional[str]:
        return self._zscale.dst_matrix

    @dst_color_space.setter
    def dst_color_space(self, val: Optional[str]):
        self._zscale.dst_matrix = ColorSpaces.ffmpeg_to_zscale(val)
        self._dst_color_primaries_meta = val
        self._dst_color_trc_meta = val
        self._dst_colorspace_meta = val

    @property
    def dst_range_full(self) -> Optional[bool]:
        return self._zscale.dst_range_full

    @dst_range_full.setter
    def dst_range_full(self, x: Optional[bool]):
        self._zscale.dst_range_full = x
        self._dst_color_range_meta = x

    @property
    def src_range_full(self) -> Optional[bool]:
        return self._zscale.src_range_full

    @src_range_full.setter
    def src_range_full(self, x: Optional[bool]):
        self._zscale.src_range_full = x

    def __iter__(self):
        # странные параметры, которые определяют "метаданные" результирующего
        # видео. В итоге оно при кодировании выглядит например как
        # (tv, bt709, progressive), а не (unknown/unknown/unknown, progressive)

        zscale_str = str(self._zscale)
        if zscale_str:
            yield "-vf"
            yield zscale_str

        if self._dst_colorspace_meta is not None:
            yield '-colorspace'
            yield self._dst_colorspace_meta

        if self._dst_color_primaries_meta is not None:
            yield '-color_primaries'
            yield self._dst_color_primaries_meta
        if self._dst_color_trc_meta is not None:
            yield '-color_trc'
            yield self._dst_color_trc_meta

        if self._dst_color_range_meta is not None:
            # https://trac.ffmpeg.org/ticket/443
            # "0" auto, "1" 16-235, "2" 0-255
            yield '-color_range'
            yield '2' if self._dst_color_range_meta else '1'

        yield '-movflags'
        yield '+write_colr'

    def __str__(self):
        return ' '.join(iter(self))


