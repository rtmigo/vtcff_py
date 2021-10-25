# [vtcff](https://github.com/rtmigo/vtcff_py)

**This project is a draft 🍏 and is not intended to be used by anyone.**

`vtcff` is a library for transcoding between video formats with an emphasis on
maintaining quality and color depth in studio pipelines.

It generates arguments for `ffmpeg` – the least intuitive command line tool ever
created.

# Install

```bash
$ pip3 install git+https://github.com/rtmigo/vtcff_py#egg=vtcff
```

This command will install the package, but not
[ffmpeg](https://www.ffmpeg.org/) itself.

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
cmd.dst_codec_video = Hevc()

# run command
subprocess.check_call(list(cmd))
```

# Getting the generated arguments

```python3
import subprocess, os
from vtcff import FfmpegCommand, Hevc

cmd = FfmpegCommand()
cmd.src_file = 'source.mov'
cmd.dst_file = 'target.mov'
cmd.dst_codec_video = Hevc()

print(str(cmd))
# ffmpeg -i source.mov -vcodec libx265 target.mov

print(list(cmd))
# ['ffmpeg', '-i', 'source.mov', '-vcodec', 'libx265', 'target.mov']

# running in different ways:
os.system(str(cmd))
subprocess.run(list(cmd))
```

# zscale vs scale

`ffmpeg` has two filters for color and frame size conversions:
- [`scale`](https://ffmpeg.org/ffmpeg-filters.html#scale-1) ([libswscale](https://ffmpeg.org/libswscale.html)) is more versatile 
- [`zscale`](https://ffmpeg.org/ffmpeg-filters.html#zscale-1) ([zimg](https://github.com/sekrit-twc/zimg)) gives a more predictable quality

By default, `vtcff` uses `zscale`. Sometimes it may lead to error "no path between colorspaces". This error would 
not occur with `scale`.

To switch to the `scale`, create object like this: 

```python3
from vtcff import FfmpegCommand

cmd = FfmpegCommand(use_zscale=False)  # will use scale (libswscale)   
```

No other code changes are required.

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

# use zscale (zimg) for color conversions
cmd = FfmpegCommand()

# Full/Data/PC range to Limited/Video/TV
cmd.src_range_full = True
cmd.dst_range_full = False

# rec.709 to rec.2020 
cmd.src_color_space = 'bt709'
cmd.dst_color_space = 'bt2020'
```

# Set some arguments manually

Manual arguments override those generated by the object.

```python3
from vtcff import FfmpegCommand

cmd = FfmpegCommand()

# set arguments as string
cmd.override_video.string = "-vcodec libx265"
cmd.override_video.string += "-x265-params lossless=1"

# or as list
cmd.override_video.list = ["-vcodec", "libx265"]
cmd.override_video.list.extend(["-x265-params", "lossless=1"])

# video, audio and general are three independent groups arguments
cmd.override_video.string = "-vcodec libx265"
cmd.override_audio.string = "-c:a aac -cutoff 18000 -b:a 128K"
cmd.override_general.string = "-movflags write_colr"

# so you can modify one of the groups without touching the others
cmd.override_video.string = "-vcodec prores_ks -profile:v 3"
```

# Timelapse

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
