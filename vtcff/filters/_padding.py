from typing import NamedTuple, Union


class Pad(NamedTuple):
    # значениями полей может быть размер или что-то вроде "iw+10"
    left: Union[int, str] = 0
    top: Union[int, str] = 0
    width: Union[int, str] = 0
    height: Union[int, str] = 0
    color: str = 'black'

    def __str__(self):
        return "_pad=width=%s:height=%s:x=%s:y=%s:color=%s" \
               % (self.width, self.height, self.left, self.top, self.color)

    # def cropRect(self, rectPosX, rectPosY, rectWidth, rectHeight):
    #     cropFilter = "crop=%s:%s:%s:%s" % (
    #         rectWidth, rectHeight, rectPosX, rectPosY)
