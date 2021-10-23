import unittest

from vtcff._ffmpeg_base import VtcFfmpegCommand
from vtcff.filters._transpose import Transpose
from vtcff.filters.common import Scaling


def rindex(alist, value):
    return len(alist) - alist[-1::-1].index(value) - 1


class TestCommand(unittest.TestCase):

    def create_default(self, zscale=False) -> VtcFfmpegCommand:
        cmd = VtcFfmpegCommand(use_zscale=zscale)
        cmd.src_file = "/tmp/path/to/src.mov"
        cmd.dst_file = "/tmp/path/to/dst.mov"
        return cmd

    def test_ffmpeg_is_first_arg(self):
        cmd = self.create_default()
        self.assertEqual(list(cmd)[0], 'ffmpeg')

    def test_src_file_is_in_args(self):
        cmd = self.create_default()
        self.assertIn(cmd.src_file, list(cmd))

    def test_dst_file_is_last_arg(self):
        cmd = self.create_default()
        self.assertEqual(cmd.dst_file, list(cmd)[-1])

    def test_framerate_before_i(self):
        cmd = self.create_default()
        cmd.src_fps = 30
        args = list(cmd)
        self.assertLess(args.index('-framerate'), args.index('-i'))
        self.assertLess(args.index('-r'), args.index('-i'))

    def test_gamma_before_i(self):
        cmd = self.create_default()
        cmd.src_gamma = 2.2
        args = list(cmd)
        self.assertLess(args.index('-gamma'), args.index('-i'))

    def test_dst_range_limited(self):
        cmd = self.create_default(zscale=True)
        expected = ['range=limited',
                    '-color_range 1']
        self.assert_none_in(expected, str(cmd))

        cmd.dst_range_full = False
        self.assert_all_in(expected, str(cmd))

        cmd.dst_range_full = None
        self.assert_none_in(expected, str(cmd))

    def test_dst_range_full(self):
        cmd = self.create_default(zscale=True)
        expected = ['range=full',
                    '-color_range 2']
        self.assert_none_in(expected, str(cmd))

        cmd.dst_range_full = True
        self.assert_all_in(expected, str(cmd))

        cmd.dst_range_full = None
        self.assert_none_in(expected, str(cmd))

    def test_range_full_to_limited(self):
        cmd = self.create_default(zscale=True)
        addend = "rangein=full:range=limited"
        self.assertNotIn(addend, str(cmd))
        cmd.src_range_full = True
        cmd.dst_range_full = False
        self.assertIn(addend, str(cmd))

    def assert_all_in(self, items, where):
        for x in items:
            self.assertIn(x, where)

    def assert_none_in(self, items, where):
        for x in items:
            self.assertNotIn(x, where)

    def test_color_spaces(self):
        cmd = self.create_default(zscale=True)

        expected = ['-colorspace bt709',
                    '-color_primaries bt709',
                    '-color_trc bt709',
                    '-vf',
                    'matrix=709']

        self.assert_none_in(expected, str(cmd))

        cmd.dst_color_space = 'bt709'
        self.assert_all_in(expected, str(cmd))

        cmd.dst_color_space = None
        self.assert_none_in(expected, str(cmd))

        with self.assertRaises(ValueError):
            cmd.dst_color_space = 'labuda'

    def test_override_known_param(self):
        cmd = self.create_default(zscale=True)
        cmd.dst_color_space = 'bt709'
        self.assertIn('-colorspace bt709', str(cmd))

        cmd.override_video.list.extend(['-colorspace', 'bt2020'])
        self.assertNotIn('-colorspace bt709', str(cmd))
        self.assertIn('-colorspace bt2020', str(cmd))

        cmd.override_video.string = '-colorspace bt601'
        self.assertNotIn('-colorspace bt709', str(cmd))
        self.assertNotIn('-colorspace bt2020', str(cmd))
        self.assertIn('-colorspace bt601', str(cmd))

    def test_override_unset_param(self):
        cmd = self.create_default()
        self.assertNotIn('-eniki beniki', str(cmd))
        cmd.override_general.string = '-eniki beniki'
        self.assertIn('-eniki beniki', str(cmd))

    def test_time_range_in(self):
        cmd = self.create_default()
        expected = '-ss 2'
        self.assertNotIn(expected, str(cmd))
        cmd.dst_time_range.begin = 2
        self.assertIn(expected, str(cmd))

        # убедимся, что оно после -i
        args = list(cmd)
        self.assertGreater(args.index('-ss'), rindex(args, '-i'))

    def test_time_range_duration(self):
        cmd = self.create_default()
        expected = '-t 10'
        self.assertNotIn(expected, str(cmd))
        cmd.dst_time_range.duration = 10
        self.assertIn(expected, str(cmd))

        # убедимся, что оно после -i
        args = list(cmd)
        self.assertGreater(args.index('-t'), rindex(args, '-i'))

    def test_time_range_in_none_zero(self):
        cmd = self.create_default()

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
            self.assertGreater(args.index('-ss'), rindex(args, '-i'))

    def test_transpose(self):
        cmd = self.create_default()
        expected = '-vf transpose=2'
        self.assertNotIn(expected, str(cmd))
        cmd.transpose = Transpose.CounterClockwise
        self.assertEqual(cmd.transpose, Transpose.CounterClockwise)
        self.assertIn(expected, str(cmd))

    def test_swscale_scale(self):
        # todo test swscale quality flags
        with self.subTest("Constant"):
            cmd = self.create_default()
            expected = '-vf scale=1920:1080'
            self.assertNotIn(expected, str(cmd))
            scaling = Scaling(1920, 1080, False)
            cmd.scaling = scaling
            self.assertEqual(cmd.scaling, scaling)
            self.assertIn(expected, str(cmd))
            self.assert_sws_flags(cmd)

        with self.subTest("Downscale both"):
            cmd = self.create_default()
            expected = "-vf scale='min(iw,1920)':'min(ih,1080)'"
            self.assertNotIn(expected, str(cmd))
            scaling = Scaling(1920, 1080, True)
            cmd.scaling = scaling
            self.assertEqual(cmd.scaling, scaling)
            self.assertIn(expected, str(cmd))
            self.assert_sws_flags(cmd)

        with self.subTest("Downscale height"):
            cmd = self.create_default()
            expected = "-vf scale=-2:'min(ih,1080)'"
            self.assertNotIn(expected, str(cmd))
            scaling = Scaling(-2, 1080, True)
            cmd.scaling = scaling
            self.assertEqual(cmd.scaling, scaling)
            self.assertIn(expected, str(cmd))
            self.assert_sws_flags(cmd)

        with self.subTest("Downscale width"):
            cmd = self.create_default()
            expected = "-vf scale='min(iw,1920)':-1"
            self.assertNotIn(expected, str(cmd))
            scaling = Scaling(1920, -1, True)
            cmd.scaling = scaling
            self.assertEqual(cmd.scaling, scaling)
            self.assertIn(expected, str(cmd))
            self.assert_sws_flags(cmd)

    def assert_sws_flags(self, cmd):
        self.assertIn(
            '-sws_flags spline+accurate_rnd+full_chroma_int+full_chroma_inp',
            str(cmd))

    def test_zscale_scale(self):
        with self.subTest("Constant"):
            cmd = self.create_default(zscale=True)
            expected = '-vf zscale=filter=spline36:w=1920:h=1080'
            self.assertNotIn(expected, str(cmd))
            scaling = Scaling(1920, 1080, False)
            cmd.scaling = scaling
            self.assertEqual(cmd.scaling, scaling)
            self.assertIn(expected, str(cmd))
            self.assert_sws_flags(cmd)
