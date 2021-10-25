# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT
import random
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

from tests.common import create_test_cmd, unique_item_after
from vtcff import Crop, FfmpegCommand, Hevc, Avc
from vtcff import HevcLosslessAndNearLosslessError, \
    HevcBitrateSpecifiedForLosslessError
from vtcff._codec_avc_preset import VcPreset
from vtcff._codec_prores_ks import Prores, ProresProfile
from vtcff._common import Scale
from vtcff._filter_transpose import Transpose


def last_index(alist: List, value) -> int:
    result = len(alist) - alist[-1::-1].index(value) - 1
    if result < 0:
        raise ValueError("item not found")
    return result


def first_index(alist: List, value) -> int:
    result = alist.index(value)
    if result < 0:
        raise ValueError("item not found")
    return result


class BaseTest(unittest.TestCase):
    def assertAllIn(self, items, where):
        for x in items:
            self.assertIn(x, where)

    def assertNoneIn(self, items, where):
        for x in items:
            self.assertNotIn(x, where)

    def assertSwsFlags(self, cmd: FfmpegCommand):
        self.assertIn(
            '-sws_flags spline+accurate_rnd+full_chroma_int+full_chroma_inp',
            str(cmd))


class TestInputArg(BaseTest):
    def test_input_directory_as_frames(self):
        with TemporaryDirectory() as tds:
            td = Path(tds)
            (td / "frame0001.png").touch()
            (td / "frame0002.png").touch()
            (td / "frame0003.png").touch()

            cmd = FfmpegCommand()
            cmd.src_file = td
            cmd.dst_file = "/tmp/file.mov"

            self.assertTrue(any(arg.endswith('frame%04d.png') for arg in cmd),
                            list(cmd))


class TestProres(BaseTest):
    def test_prores(self):
        cmd = create_test_cmd()
        items = ['-vcodec prores_ks', '-profile:v 2']
        self.assertNoneIn(items, str(cmd))
        cmd.dst_codec_video = Prores()
        self.assertAllIn(items, str(cmd))

    def test_prores_hq(self):
        cmd = create_test_cmd()
        items = ['-vcodec prores_ks', '-profile:v 3']
        self.assertNoneIn(items, str(cmd))
        cmd.dst_codec_video = Prores(profile=ProresProfile.HQ)
        self.assertAllIn(items, str(cmd))

    def test_prores_vendor(self):
        cmd = create_test_cmd()
        items = ['-vcodec prores_ks', '-vendor apl0']
        self.assertNoneIn(items, str(cmd))
        cmd.dst_codec_video = Prores(spoof_vendor=True)
        self.assertAllIn(items, str(cmd))

    def test_prores_qscale(self):
        cmd = create_test_cmd()
        items = ['-vcodec prores_ks', '-q:v 5']
        self.assertNoneIn(items, str(cmd))
        cmd.dst_codec_video = Prores(qscale=5)
        self.assertAllIn(items, str(cmd))


class TestHevc(BaseTest):
    def test_base(self):
        cmd = create_test_cmd()
        items = ['-vcodec libx265']
        self.assertNoneIn(items, str(cmd))
        cmd.dst_codec_video = Hevc(mbps=100)
        self.assertAllIn(items, str(cmd))

    def test_preset(self):
        cmd = create_test_cmd()
        items = ['-vcodec libx265', '-preset superfast']
        self.assertNoneIn(items, str(cmd))
        cmd.dst_codec_video = Hevc(mbps=100, preset=VcPreset.N2_SUPERFAST)
        self.assertAllIn(items, str(cmd))

    def test_lossless(self):
        cmd = create_test_cmd()
        items = ['-vcodec libx265', '-x265-params', 'lossless=1']
        self.assertNoneIn(items, str(cmd))
        cmd.dst_codec_video = Hevc(lossless=True)
        self.assertAllIn(items, str(cmd))
        self.assertEqual(unique_item_after(cmd, "-preset"), 'ultrafast')

    def test_near_lossless(self):
        cmd = create_test_cmd()
        items = ['-vcodec libx265', '-x265-params',
                 'cu-lossless=1:psy-rd=1.0:rd=3']
        self.assertNoneIn(items, str(cmd))
        cmd.dst_codec_video = Hevc(near_lossless=True, mbps=100)
        self.assertAllIn(items, str(cmd))
        self.assertEqual(unique_item_after(cmd, "-preset"), 'placebo')

    def test_bitrate(self):
        cmd = create_test_cmd()
        items = ['-vcodec libx265', '-x265-params', 'bitrate=123500']
        self.assertNoneIn(items, str(cmd))
        cmd.dst_codec_video = Hevc(mbps=123.5)
        self.assertAllIn(items, str(cmd))

    def test_lossless_and_near_losseless_cannot_be_used_both(self):
        with self.assertRaises(HevcLosslessAndNearLosslessError):
            list(Hevc(lossless=True, near_lossless=True).args())

    def test_either_lossless_or_bitrate(self):
        with self.assertRaises(HevcBitrateSpecifiedForLosslessError):
            list(Hevc(lossless=True, mbps=100).args())


class TestAvc(BaseTest):
    def test_base(self):
        cmd = create_test_cmd()
        items = ['-vcodec libx264']
        self.assertNoneIn(items, str(cmd))
        cmd.dst_codec_video = Avc()
        self.assertAllIn(items, str(cmd))

    def test_preset(self):
        cmd = create_test_cmd()
        items = ['-vcodec libx264', '-preset fast']
        self.assertNoneIn(items, str(cmd))
        cmd.dst_codec_video = Avc(preset=VcPreset.N5_FAST)
        self.assertAllIn(items, str(cmd))


class TestsZscale(BaseTest):

    def test_spline36_is_default(self):
        cmd = create_test_cmd()

        expected = ['filter=spline36',
                    'zscale=']

        self.assertNoneIn(expected, str(cmd))
        cmd.scale = Scale(1920, 1080)
        self.assertAllIn(expected, str(cmd))

    def test_zscale_is_default(self):
        cmd = FfmpegCommand()
        cmd.src_file = "a"
        cmd.dst_file = "b"
        self.assertTrue(cmd._use_zscale)
        cmd.scale = Scale(2048, 1920)
        self.assertIn("zscale=", str(cmd))

    def test_error_diffusion_is_default(self):
        cmd = create_test_cmd()

        expected = ['dither=error_diffusion',
                    'zscale=']

        self.assertNoneIn(expected, str(cmd))

        cmd.dst_range_full = True
        cmd.dst_range_full = False

        self.assertAllIn(expected, str(cmd))

    def test_zscale_scale(self):
        cmd = create_test_cmd()

        expected = ['filter=spline36',
                    'w=1920:h=1080']

        self.assertNoneIn(expected, str(cmd))

        scaling = Scale(1920, 1080, False)
        cmd.scale = scaling
        self.assertEqual(cmd.scale, scaling)

        self.assertAllIn(expected, str(cmd))


class TestCommand(BaseTest):

    def test_ffmpeg_is_first_arg(self):
        cmd = create_test_cmd()
        self.assertEqual(list(cmd)[0], 'ffmpeg')

    def test_src_file_is_in_args(self):
        cmd = create_test_cmd()
        self.assertIn(cmd.src_file, list(cmd))

    def test_dst_file_is_last_arg(self):
        cmd = create_test_cmd()
        self.assertEqual(cmd.dst_file, list(cmd)[-1])

    def test_framerate_before_i(self):
        cmd = create_test_cmd()
        cmd.src_fps = 30
        args = list(cmd)
        self.assertLess(args.index('-framerate'), args.index('-i'))
        self.assertLess(args.index('-r'), args.index('-i'))

    def test_gamma_before_i(self):
        cmd = create_test_cmd()
        cmd.src_gamma = 2.2
        args = list(cmd)
        self.assertLess(args.index('-gamma'), args.index('-i'))

    def test_dst_range_limited(self):
        cmd = create_test_cmd(zscale=True)
        expected = ['range=limited',
                    '-color_range 1']
        self.assertNoneIn(expected, str(cmd))

        cmd.dst_range_full = False
        self.assertAllIn(expected, str(cmd))

        cmd.dst_range_full = None
        self.assertNoneIn(expected, str(cmd))

    def test_dst_range_full(self):
        cmd = create_test_cmd(zscale=True)
        expected = ['range=full',
                    '-color_range 2']
        self.assertNoneIn(expected, str(cmd))

        cmd.dst_range_full = True
        self.assertAllIn(expected, str(cmd))

        cmd.dst_range_full = None
        self.assertNoneIn(expected, str(cmd))

    def test_range_full_to_limited(self):
        cmd = create_test_cmd(zscale=True)
        addend = "rangein=full:range=limited"
        self.assertNotIn(addend, str(cmd))
        cmd.src_range_full = True
        cmd.dst_range_full = False
        self.assertIn(addend, str(cmd))

    def test_color_spaces(self):
        cmd = create_test_cmd(zscale=True)

        expected = ['-colorspace bt709',
                    '-color_primaries bt709',
                    '-color_trc bt709',
                    '-vf',
                    'matrix=709']

        self.assertNoneIn(expected, str(cmd))

        cmd.dst_color_space = 'bt709'
        self.assertAllIn(expected, str(cmd))

        cmd.dst_color_space = None
        self.assertNoneIn(expected, str(cmd))

        with self.assertRaises(ValueError):
            cmd.dst_color_space = 'labuda'

    def test_override_known_param(self):
        cmd = create_test_cmd(zscale=True)
        cmd.dst_color_space = 'bt709'
        self.assertIn('-colorspace bt709', str(cmd))

        cmd.custom.video.list.extend(['-colorspace', 'bt2020'])
        self.assertNotIn('-colorspace bt709', str(cmd))
        self.assertIn('-colorspace bt2020', str(cmd))

        cmd.custom.video.string = '-colorspace bt601'
        self.assertNotIn('-colorspace bt709', str(cmd))
        self.assertNotIn('-colorspace bt2020', str(cmd))
        self.assertIn('-colorspace bt601', str(cmd))

    def test_override_unset_param(self):
        cmd = create_test_cmd()
        self.assertNotIn('-eniki beniki', str(cmd))
        cmd.custom.after_i.string = '-eniki beniki'
        self.assertIn('-eniki beniki', str(cmd))

    def test_custom_before_i(self):
        cmd = create_test_cmd()
        val = "-delta 5"
        self.assertNotIn(val, str(cmd))
        cmd.custom.before_i.string = val
        self.assertIn(val, str(cmd))
        self.assertOrderIs(cmd, '-delta', '-i')

    def test_time_range_in(self):
        cmd = create_test_cmd()
        expected = '-ss 2'
        self.assertNotIn(expected, str(cmd))
        cmd.dst_time_range.begin = 2
        self.assertIn(expected, str(cmd))

        # убедимся, что оно после -i
        self.assertOrderIs(cmd, '-i', '-ss')

    def test_time_range_duration(self):
        cmd = create_test_cmd()
        expected = '-t 10'
        self.assertNotIn(expected, str(cmd))
        cmd.dst_time_range.duration = 10
        self.assertIn(expected, str(cmd))

        # убедимся, что оно после -i
        self.assertOrderIs(cmd, '-i', '-t')
        # self.assertGreater(last_index(args, '-t'), first_index(args, '-i'))

    def assertOrderIs(self, items, left, right):
        items = list(items)
        self.assertLess(last_index(items, left), first_index(items, right))

    def test_time_range_in_none_zero(self):
        cmd = create_test_cmd()

        with self.subTest("none"):
            cmd.dst_time_range.begin = None
            self.assertNotIn('-ss', str(cmd))
        with self.subTest("zero"):
            cmd.dst_time_range.begin = 0
            self.assertNotIn('-ss', str(cmd))

        with self.subTest("1"):
            cmd.dst_time_range.begin = 1
            self.assertIn('-ss', str(cmd))

            # убедимся, что оно после -i
            args = list(cmd)
            self.assertGreater(args.index('-ss'), last_index(args, '-i'))

    def test_transpose(self):
        cmd = create_test_cmd()
        expected = '-vf transpose=2'
        self.assertNotIn(expected, str(cmd))
        cmd.transpose = Transpose.COUNTER_CLOCKWISE
        self.assertEqual(cmd.transpose, Transpose.COUNTER_CLOCKWISE)
        self.assertIn(expected, str(cmd))

    def test_swscale_scale(self):
        # todo test swscale quality flags
        with self.subTest("Constant"):
            cmd = create_test_cmd(zscale=False)
            expected = '-vf scale=width=1920:height=1080'
            self.assertNotIn(expected, str(cmd))
            scaling = Scale(1920, 1080, False)
            cmd.scale = scaling
            self.assertEqual(cmd.scale, scaling)
            self.assertIn(expected, str(cmd))
            self.assertSwsFlags(cmd)

        with self.subTest("Downscale both"):
            cmd = create_test_cmd(zscale=False)
            expected = "-vf scale=width='min(iw,1920)':height='min(ih,1080)'"
            self.assertNotIn(expected, str(cmd))
            scaling = Scale(1920, 1080, True)
            cmd.scale = scaling
            self.assertEqual(cmd.scale, scaling)
            self.assertIn(expected, str(cmd))
            self.assertSwsFlags(cmd)

        with self.subTest("Downscale height"):
            cmd = create_test_cmd(zscale=False)
            expected = "-vf scale=width=-2:height='min(ih,1080)'"
            self.assertNotIn(expected, str(cmd))
            scaling = Scale(-2, 1080, True)
            cmd.scale = scaling
            self.assertEqual(cmd.scale, scaling)
            self.assertIn(expected, str(cmd))
            self.assertSwsFlags(cmd)

        with self.subTest("Downscale width"):
            cmd = create_test_cmd(zscale=False)
            expected = "-vf scale=width='min(iw,1920)':height=-1"
            self.assertNotIn(expected, str(cmd))
            scaling = Scale(1920, -1, True)
            cmd.scale = scaling
            self.assertEqual(cmd.scale, scaling)
            self.assertIn(expected, str(cmd))
            self.assertSwsFlags(cmd)

    def test_switch_zscale_to_swscale(self):
        cmd = create_test_cmd(zscale=True)

        self.assertNotIn('1920', str(cmd))
        cmd.scale = Scale(1920, 1080)

        self.assertIn('1920', str(cmd))
        self.assertNotIn('-vf scale=', str(cmd))
        self.assertIn('-vf zscale=', str(cmd))

        cmd.use_zscale = False
        self.assertIn('1920', str(cmd))
        self.assertIn('-vf scale=', str(cmd))
        self.assertNotIn('-vf zscale=', str(cmd))

        cmd.use_zscale = True
        self.assertIn('1920', str(cmd))
        self.assertNotIn('-vf scale=', str(cmd))
        self.assertIn('-vf zscale=', str(cmd))

    def test_switch_zscale_to_swscale_random(self):

        def random_bool():
            return random.choice((True, False))

        cmd = create_test_cmd()
        for _ in range(10):
            scale = Scale(width=random.randint(100, 200),
                          height=random.randint(100, 200),
                          downscale_only=random_bool())
            src_range_full = random_bool()
            dst_range_full = random_bool()
            src_color = random.choice(('bt709', 'bt2020'))
            dst_color = random.choice(('bt709', 'bt2020'))

            cmd.scale = scale
            cmd.src_range_full = src_range_full
            cmd.dst_range_full = dst_range_full
            cmd.src_color_space = src_color
            cmd.dst_color_space = dst_color

            cmd.use_zscale = random_bool()

            self.assertEqual(cmd.scale, scale)
            self.assertEqual(cmd.src_color_space, src_color)
            self.assertEqual(cmd.dst_color_space, dst_color)
            self.assertEqual(cmd.src_range_full, src_range_full)
            self.assertEqual(cmd.dst_range_full, dst_range_full)

            if cmd.use_zscale:
                self.assertNotIn('-vf scale=', str(cmd))
                self.assertIn('-vf zscale=', str(cmd))
            else:
                self.assertIn('-vf scale=', str(cmd))
                self.assertNotIn('-vf zscale=', str(cmd))

    def test_crop(self):
        cmd = create_test_cmd(zscale=True)
        expected = '-vf crop=100:200:10:20'
        self.assertNotIn(expected, str(cmd))
        c = Crop(10, 20, 100, 200)
        cmd.crop = c
        self.assertEqual(cmd.crop, c)
        self.assertIn(expected, str(cmd))
        self.assertSwsFlags(cmd)

    def test_pixfmt(self):
        cmd = create_test_cmd(zscale=True)
        cmd.dst_pixfmt = "yuvj420p"
        self.assertEqual(unique_item_after(cmd, "-pix_fmt"), "yuvj420p")
