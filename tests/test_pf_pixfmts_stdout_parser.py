# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

import unittest

from vtcff._pf_10_pixfmts_stdout_parser import _pix_fmts_tuples, pixfmt_to_spec, \
    pixfmt_alpha


class TestPixFmts(unittest.TestCase):
    def test_read_tuples(self):
        lst = _pix_fmts_tuples("ffmpeg")
        self.assertGreater(len(lst), 5)
        z = next(x for x in lst if x.name == "yuv422p10le")
        self.assertEqual(z.bits_per_pixel, 20)
        self.assertEqual(z.nb_components, 3)
        self.assertEqual(z.flags, 'IO...')

    def test_get_by_name(self):
        z = pixfmt_to_spec('yuva444p10le', ffmpeg_exe="ffmpeg")
        self.assertEqual(z.name, 'yuva444p10le')
        self.assertEqual(z.bits_per_pixel, 40)

        with self.assertRaises(KeyError):
            pixfmt_to_spec('abcd', ffmpeg_exe="ffmpeg")


class TestAlpha(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(pixfmt_alpha('yuva444p10le', ffmpeg_exe="ffmpeg"), True)
        self.assertEqual(pixfmt_alpha('yuv422p10le', ffmpeg_exe="ffmpeg"), False)
        self.assertEqual(pixfmt_alpha('ya8', ffmpeg_exe="ffmpeg"), None)
