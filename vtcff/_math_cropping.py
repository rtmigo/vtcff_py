# SPDX-FileCopyrightText: (c) 2016-2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from typing import Tuple

from vtcff._filter_crop import Crop
from ._command import FfmpegCommand, Scale


def crop_height(width, aspect: Tuple[int, int], div=1):
    # print("crop_height %dxX->%d:%d"%(width,aspectPair[0],aspectPair[1]))

    # aspectPair - это FrameSize, обозначающий желаемое соотношение сторон:
    # (1920,1080) или просто (16,9).
    # width - фиксированная ширина будущего кадра.
    # Метод подбирает соответствующую такой ширине высоту.
    #
    # Сложность в том, что ширина и высота у нас по определению числа целые,
    # а aspect - дробное. Поэтому примерно мы ищем такой результат:
    #   w/h = aspect
    #   w/aspect = round(h)
    #   h*aspect = round(w)
    #
    # Но и это не всегда возможно. Например, целевые пропорции это 4096x2160.
    # Фиксированная ширина кадра 5472. Дробное значение соответствующей высоты
    # - 2885.625. В зависимости способа от округления высоты, заданной
    # пропорции будут соответствовать два разрешения:
    #   5470.81 x 2885
    #   5472.71 x 2886
    # Тут очевидно, что изменилась ширина, как ее ни округляй.
    #
    # Поэтому мы подбираем не только высоту, но и ширину уменьшаем до тех пор,
    # пока на найдем пару WxH, соответствующую требованиям.

    aspect_f = aspect[0] / aspect[1]

    for w in range(width, 0, -1):

        if w % div != 0:
            continue

        h = int(round(w / aspect_f))

        if h % div != 0:
            continue

        if round(h * aspect_f) == w:
            return w, h

    return None, None


def crop_width(height, aspect: Tuple[int, int], div=1):
    # меняем местами ширину и высоту
    rotatedAspect = aspect[1], aspect[0]
    rotatedWidth = height

    # находим размер
    rotatedResult = crop_height(rotatedWidth, rotatedAspect,
                                div=div)

    # снова меняем местами
    return rotatedResult[1], rotatedResult[0]


def crop_size(src_size: Tuple[int, int], dst_aspect: Tuple[int, int], div=1):
    # targetAspectPair - два числа, сообщающие о желаемых пропорциях размера кадра.
    # sourceSize - исходный размер кадра.
    # Возвращается максимальный по размер кропнутый кадр нужных пропорций.

    sourceAspect = src_size[0] / src_size[1]
    targetAspect = dst_aspect[0] / dst_aspect[1]

    sourceWidth = src_size[0]
    sourceHeight = src_size[1]

    if sourceAspect > targetAspect:
        # нужно обрезать края слева и справа
        result = crop_width(sourceHeight, dst_aspect,
                            div=div)
    elif sourceAspect < targetAspect:
        # нужно обрезать края сверху и снизу
        result = crop_height(sourceWidth, dst_aspect,
                             div=div)
    else:
        # пропорции и так соответствуют
        result = src_size

    assert result[0] <= src_size[0] and result[1] <= src_size[1]
    return result


def whwh_to_xywh(sourceWidth, sourceHeight,
                 targetWidth, targetHeight,
                 alignX="M", alignY="M"):
    # Два этапа:
    #   1. Отрезаем от исходника лишние пиксели, сделав пропорции
    #   такими, как надо.
    #   2. Пропорционально уменьшаем оставшийся прямоугольник.

    croppedSize = crop_size((sourceWidth, sourceHeight),
                            (targetWidth, targetHeight), div=1)
    # в этом вызове функции мы использовали (targetWidth,targetHeight)
    # как целевые пропорции, а не целевое разрешение. Функция вернула что-то
    # по возможности близкое к первому аргументу, а не ко второму.

    widthDelta = sourceWidth - croppedSize[0]
    heightDelta = sourceHeight - croppedSize[1]

    assert widthDelta >= 0
    assert heightDelta >= 0

    cropTop = 0
    cropBottom = 0
    cropLeft = 0
    cropRight = 0

    if widthDelta > 0:
        if alignX == "M":
            halfWidthDelta = int(round(widthDelta / 2))
            cropLeft = halfWidthDelta
            cropRight = widthDelta - cropLeft
        elif alignX == "L":
            cropRight = widthDelta
            cropLeft = 0
        elif alignX == "R":
            cropLeft = widthDelta
            cropRight = 0
        else:
            raise Exception("Unexpected alignX value: %s." % alignX)

    if heightDelta > 0:
        if alignY == "M":
            halfHeightDelta = int(round(heightDelta / 2))
            cropTop = halfHeightDelta
            cropBottom = heightDelta - cropTop
        elif alignY == "T":
            cropBottom = heightDelta
            cropTop = 0
        elif alignY == "B":
            cropTop = heightDelta
            cropBottom = 0
        else:
            raise Exception("Unexpected alignY value: %s." % alignY)

    croppedWidth = sourceWidth - cropLeft - cropRight
    croppedHeight = sourceHeight - cropTop - cropBottom

    # croppedHeight+=1
    # tmpAspect = croppedWidth / croppedHeight
    # logger.info(
    #     "sourceWidth=%d, cropLeft=%d, cropRight=%d, croppedWidth=%d" % (
    #         sourceWidth, cropLeft, cropRight, croppedWidth))
    # logger.info(
    #     "sourceHeight=%d, cropTop=%d, cropBottom=%d, croppedHeight=%d" % (
    #         sourceHeight, cropTop, cropBottom, croppedHeight))
    # logger.info("croppedWidth/croppedHeight=%d/%d=%.5f" % (
    #     croppedWidth, croppedHeight, croppedWidth / croppedHeight))
    # logger.info("finalHeight %d => finalWidth %.4f" % (
    #     targetHeight, targetHeight * tmpAspect))

    # баг-2016? При размере кропнутой картинки 5471:2885 и scale=-1:2160 ffmpeg
    # почему-то вычислял ширину целевого кадра как 4095, хотя арифметически
    # ширина должна была получиться 2160*(5471/2885) = 4096.1386. Это
    # выяснилось для отдельного видео, которое из размера 5472x3076 я
    # хотел сконвертить в 4096x2160.
    #
    # Чтобы исправить проблему, я просто заменил scale=-1:2160 на
    # scale=-2:2160. Как именно ffmpeg станет это округлять - не проверил

    assert round((sourceWidth - cropLeft - cropRight) / (
            sourceHeight - cropTop - cropBottom)) == round(
        targetWidth / targetHeight)

    return cropLeft, cropTop, croppedWidth, croppedHeight


def crop_and_scale(cmd: FfmpegCommand,
                   src_width, src_height,
                   dst_width, dst_height,
                   align_x="M", align_y="M"):
    x, y, w, h = whwh_to_xywh(sourceWidth=src_width,
                              sourceHeight=src_height,
                              targetWidth=dst_width,
                              targetHeight=dst_height, alignX=align_x,
                              alignY=align_y)
    cmd.crop = Crop(left=x, top=y, width=w, height=h)
    cmd.scale = Scale(-2, dst_height)
