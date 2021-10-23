import unittest

from vtcff._ffmpeg_base import VtcFfmpegCommand


class TestCommand(unittest.TestCase):

    def create_default(self) -> VtcFfmpegCommand:
        cmd = VtcFfmpegCommand()
        cmd.inputFile = "/path/to/src.mov"
        cmd.outputfile = "/path/to/dst.mp4"
        return cmd

    def test_dst_range_limited(self):
        cmd = self.create_default()
        expected = ['range=limited',
                    '-color_range 1']
        self.assert_none_in(expected, str(cmd))

        cmd.dst_range_full = False
        self.assert_all_in(expected, str(cmd))

        cmd.dst_range_full = None
        self.assert_none_in(expected, str(cmd))

    def test_dst_range_full(self):
        cmd = self.create_default()
        expected = ['range=full',
                    '-color_range 2']
        self.assert_none_in(expected, str(cmd))

        cmd.dst_range_full = True
        self.assert_all_in(expected, str(cmd))

        cmd.dst_range_full = None
        self.assert_none_in(expected, str(cmd))

    def test_range_full_to_limited(self):
        cmd = self.create_default()
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
        cmd = self.create_default()

        expected = ['-colorspace bt709',
                    '-color_primaries bt709',
                    '-color_trc bt709',
                    'matrix=709']

        self.assert_none_in(expected, str(cmd))

        cmd.dst_color_space = 'bt709'
        self.assert_all_in(expected, str(cmd))

        cmd.dst_color_space = None
        self.assert_none_in(expected, str(cmd))

        with self.assertRaises(ValueError):
            cmd.dst_color_space = 'labuda'

    def test_override_known_param(self):
        cmd = self.create_default()
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

