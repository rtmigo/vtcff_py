import unittest

from vtcff._pf_15_pixfmt_subsampling import pixfmt_subsampling


class TestGuessSubsampling(unittest.TestCase):
    def test(self):
        self.assertEqual(pixfmt_subsampling('yuva444p12be'), '444')
        self.assertEqual(pixfmt_subsampling('yuva422p12be'), '422')
        self.assertEqual(pixfmt_subsampling('yuv420p'), '420')
        self.assertEqual(pixfmt_subsampling('rgba24'), '444')
        self.assertEqual(pixfmt_subsampling('weird'), None)