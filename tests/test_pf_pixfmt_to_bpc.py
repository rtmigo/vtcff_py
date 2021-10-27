# SPDX-FileCopyrightText: (c) 2016-2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

import unittest

from vtcff._pf_20_pixfmt_bpc import _guess_bpc, _ending, _subsampling_factor
from vtcff._pf_15_pixfmt_subsampling import _three_digits


class TestGuess(unittest.TestCase):
    def test(self):
        self.assertEqual(_guess_bpc('yuva444p12be', 4, 48), 12)
        self.assertEqual(_guess_bpc('yuvj444p', 3, 24), 8)
        self.assertEqual(_guess_bpc('yuva422p12be', 4, 36), 12)
        self.assertEqual(_guess_bpc('yuv420p16le', 3, 24), 16)
        self.assertEqual(_guess_bpc('yuv420p', 3, 12), 8)
        self.assertEqual(_guess_bpc('yuv410p', 3, 9), 8)
        self.assertEqual(_guess_bpc('yuv411p', 3, 12), 8)
        # self.assertEqual(_guess_bpc('yuv420p9be', 3, 13), 8)
        # yuv420p9be
        # 3
        # 13

        self.assertEqual(_guess_bpc('yuv444p10be', 3, 30), 10)
        self.assertEqual(_guess_bpc('yuv440p10be', 3, 20), 10)
        self.assertEqual(_guess_bpc('gbrap12be', 4, 48), 12)
        self.assertEqual(_guess_bpc('gbrapf32be', 4, 128), 32)
        self.assertEqual(_guess_bpc('rgb24', 3, 24), 8)
        self.assertEqual(_guess_bpc('gbrp10be', 3, 30), 10)

        # 3
        # 30


class TestThreeDigits(unittest.TestCase):
    def test(self):
        self.assertEqual(_three_digits('yuva444p12be'), '444')
        self.assertEqual(_three_digits('yuv420'), '420')
        self.assertEqual(_three_digits('yuv456'), None)
        self.assertEqual(_three_digits('yub4200'), None)


class TestEnding(unittest.TestCase):
    def test(self):
        self.assertEqual(_ending('x2rgb10be'), 10)
        self.assertEqual(_ending('gray9be'), 9)
        self.assertEqual(_ending('yuva420p9be'), 9)
        self.assertEqual(_ending('rgb'), None)


class TestSsFactor(unittest.TestCase):
    def test(self):
        self.assertEqual(_subsampling_factor('xyz444p', 3), 1 / 1)
        self.assertEqual(_subsampling_factor('xyz422p', 3), 2 / 3)
        self.assertEqual(_subsampling_factor('xyz440p', 3), 2 / 3)
        self.assertEqual(_subsampling_factor('xyz420p', 3), 1 / 2)
        self.assertEqual(_subsampling_factor('xyz444p', 4), 1 / 1)
        self.assertEqual(_subsampling_factor('xyz422p', 4), 3 / 4)
        self.assertEqual(_subsampling_factor('xyz420p', 4), 5 / 8)
