import unittest

from vtcff._pix_format_depth import guess_color_depth, _three_digits, _ending, \
    _subsampling_factor


class TestGuess(unittest.TestCase):
    def test(self):
        self.assertEqual(guess_color_depth('yuva444p12be', 4, 48), 12)
        self.assertEqual(guess_color_depth('yuvj444p', 3, 24), 8)
        self.assertEqual(guess_color_depth('yuva422p12be', 4, 36), 12)
        self.assertEqual(guess_color_depth('yuv420p16le', 3, 24), 16)
        self.assertEqual(guess_color_depth('yuv420p', 3, 12), 8)
        self.assertEqual(guess_color_depth('yuv410p', 3, 9), 8)
        self.assertEqual(guess_color_depth('yuv411p', 3, 12), 8)
        #self.assertEqual(guess_color_depth('yuv420p9be', 3, 13), 8)
        #yuv420p9be
        #3
        #13

        self.assertEqual(guess_color_depth('yuv444p10be', 3, 30), 10)
        self.assertEqual(guess_color_depth('yuv440p10be', 3, 20), 10)
        self.assertEqual(guess_color_depth('gbrap12be', 4, 48), 12)
        self.assertEqual(guess_color_depth('gbrapf32be', 4, 128), 32)
        self.assertEqual(guess_color_depth('rgb24', 3, 24), 8)
        self.assertEqual(guess_color_depth('gbrp10be', 3, 30), 10)

        #3
        #30


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