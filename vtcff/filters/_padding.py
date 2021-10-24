class PaddingFilter:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.color = 'black'

    def __str__(self):
        return "pad=width=%s:height=%s:x=%s:y=%s:color=%s" \
               % (self.w, self.h, self.x, self.y, self.color)

    # def cropRect(self, rectPosX, rectPosY, rectWidth, rectHeight):
    #     cropFilter = "crop=%s:%s:%s:%s" % (
    #         rectWidth, rectHeight, rectPosX, rectPosY)
