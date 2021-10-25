# [vtcff](https://github.com/rtmigo/vtcff_py)

**🚧 This project is a draft and is not intended to be used by anyone.**

`vtcff` is a library for transcoding between video formats with an emphasis on
maintaining quality and color depth in video production pipelines.

It generates arguments for `ffmpeg` – the least intuitive video tool ever
created.

# Install

```bash
$ pip3 install vtcff
```

This command will install the package, but not
[ffmpeg](https://www.ffmpeg.org/) itself.

<details>
<summary>other options</summary>

#### Install pre-release from GitHub:

```bash
$ pip3 install git+https://github.com/rtmigo/vtcff_py@staging#egg=vtcff
```

</details>

# Basic example

```python3
import subprocess
from vtcff import FfmpegCommand, Scale, Transpose, Hevc

cmd = FfmpegCommand()

cmd.src_file = '/path/to/source.mov'
cmd.dst_file = '/path/to/target.mov'

# set set some filters
cmd.scale = Scale(1920, 1080)
cmd.transpose = Transpose.CLOCKWISE

# set compression format
cmd.dst_codec_video = Hevc(mbps=100)

# run command
subprocess.check_call(list(cmd))
```

# Getting the generated arguments

```python3
import subprocess, os
from vtcff import FfmpegCommand, Prores

cmd = FfmpegCommand()
cmd.src_file = 'source.mov'
cmd.dst_file = 'target.mov'
cmd.dst_codec_video = Prores()

print(str(cmd))
# ffmpeg -i source.mov -vcodec prores_ks target.mov

print(list(cmd))
# ['ffmpeg', '-i', 'source.mov', '-vcodec', 'prores_ks', 'target.mov']

# running in different ways:
os.system(str(cmd))
subprocess.run(list(cmd))
```

# Custom arguments

The object allows you to manually specify ffmpeg arguments. Arguments given in
this way take precedence over arguments generated by the object.

```python3
from vtcff import FfmpegCommand

cmd = FfmpegCommand()

# set arguments as string
cmd.custom.video.string = "-vcodec libx265"
cmd.custom.video.string += "-x265-params lossless=1"

# or as list
cmd.custom.video.list = ["-vcodec", "libx265"]
cmd.custom.video.list.extend(["-x265-params", "lossless=1"])
```

The `cmd.custom` contains four fields, that can be modified independently.

Arguments to be inserted before `-i source`:

- `custom.before_i`

Arguments to be inserted after `-i source`:

- `custom.after_i`
- `custom.video`
- `custom.audio`

# zscale vs scale

`ffmpeg` has two filters for color and frame size conversions:

- [`scale`](https://ffmpeg.org/ffmpeg-filters.html#scale-1) ([libswscale](https://ffmpeg.org/libswscale.html))
  is more versatile
- [`zscale`](https://ffmpeg.org/ffmpeg-filters.html#zscale-1) ([zimg](https://github.com/sekrit-twc/zimg))
  gives a more predictable quality

By default, `vtcff` uses `zscale`. Sometimes it may lead to error "no path
between colorspaces". This error would not occur with `scale`.

The `use_zscale` property determines which filter to use.

```python3
from vtcff import FfmpegCommand, Scale

cmd = FfmpegCommand()

assert cmd.use_zscale == True  # by default, it's 'zscale' (zimg) 
cmd.use_zscale = False  # switching to 'scale' (libswscale)

# properties affected:
cmd.scale = Scale(1920, 1080)
cmd.src_color_space = 'bt709'
cmd.dst_color_space = 'bt2020'
cmd.src_range_full = True
cmd.dst_range_full = False
```

`use_zscale=True`, means that zimg will be used for conversions
**explicitly** set by object properties. This is good because these conversions
will be of high quality.

However, **implicit** conversions may also be required. For example, before
processing 16-bit PNG with `zscale`, we need to convert the pixel format from
`rgba64be` to `gbrap16le` 🤪. Ffmpeg will do it automatically with `libswscale`.

# Crop and scale

```python3
from vtcff import FfmpegCommand, Scale, Crop

# crop 10 pixels, then scale
a = FfmpegCommand()
a.crop = Crop(left=10)
a.scale = Scale(1920, 1080)

# scale, then crop 10 pixels
b = FfmpegCommand()
b.scale = Scale(1920, 1080)
b.crop = Crop(left=10)
```

## Scale proportionally

```python3
from vtcff import FfmpegCommand, Scale

cmd = FfmpegCommand()

# set height to 1080, automatically compute width 
cmd.scale = Scale(-1, 1080)

# set height to 1080, select the width as the closest factor 
# of two to the proportional size 
cmd.scale = Scale(-2, 1080)
```

# Change color range

```python3
from vtcff import FfmpegCommand

cmd = FfmpegCommand()

# Full/Data/PC range to Limited/Video/TV
cmd.src_range_full = True
cmd.dst_range_full = False

# rec.709 to rec.2020 
cmd.src_color_space = 'bt709'
cmd.dst_color_space = 'bt2020'
```

# Target formats

## Encoding to Apple ProRes

```python3
from vtcff import FfmpegCommand, Prores, ProresProfile

cmd = FfmpegCommand()

# by default it will encode to ProRes 4:2:2
cmd.dst_codec_video = Prores()

# encode to ProRes 4:2:2 HQ instead 
cmd.dst_codec_video = Prores(profile=ProresProfile.HQ)
```

## Encoding to  HEVC (H.265)

```python3
from vtcff import FfmpegCommand, Hevc, VcPreset

cmd = FfmpegCommand()

# ideal quality
cmd.dst_codec_video = Hevc(lossless=True)

# best for bitrate quality
cmd.dst_codec_video = Hevc(near_lossless=True, mbps=100)

# default quality
cmd.dst_codec_video = Hevc(mbps=100)

# all modes can be tweaked with optional speed presets:
cmd.dst_codec_video = Hevc(mbps=100,
                           preset=VcPreset.N7_SLOW)
```

By default, the `near_lossless` is set to slowest possible
`VcPreset.N10_PLACEBO`, because we are trying to maximize quality. You will
probably want to choose a faster preset so that the result appears within a
lifetime.

By default, the `lossless` is set to fastest possible
`VcPreset.N1_ULTRAFAST`, because we are not losing any quality here. The
resulting size will be roughly comparable to ProRes HQ/XQ and the encoding time
is reasonable.

# Images to videos

Converting timelapses or CGI frame sequences to ProRes video file.

```python3
import subprocess
from vtcff import FfmpegCommand, Prores, ProresProfile

cmd = FfmpegCommand()

# input directory will be automatically transformed 
# to a pattern like '/my/dir_with_frames/img_%04.png'   
cmd.src_file = '/my/dir_with_frames'
cmd.src_fps = 29.97

cmd.dst_file = '/videos/timelapse.mov'
cmd.dst_codec_video = Prores(profile=ProresProfile.HQ)

# images usually have Full/Data/PC color range,
# but most NLEs assume that videos have Limited/Video/TV range
cmd.src_range_full = True
cmd.dst_range_full = False

# we will treat sRGB like Rec.709, 
# although it's a little sad
cmd.src_color_space = 'bt709'
cmd.dst_color_space = 'bt709'

# run command
subprocess.check_call(list(cmd))
```
