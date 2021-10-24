from ._cropping import crop_and_scale
from ._encspeed import Speed
from ._ffmpeg_base import FfmpegCommand
#from ._ffmpeg_base import FfmpegCommand as VtcFfmpegCommand  # legacy :)
from .filters._cropping import Crop
from .filters._padding import Pad
from .filters.common import Scale
from .filters._transpose import Transpose
