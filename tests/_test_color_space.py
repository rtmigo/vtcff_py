import unittest

from vtcff._colorspaces import safe_str_to_colorspace, ColorSpace, \
    safe_colorspace_to_str


class TestColorspace(unittest.TestCase):
    def test_to_colorspace(self):
        self.assertEqual(safe_str_to_colorspace('bt709'), ColorSpace.bt709)
        self.assertEqual(safe_str_to_colorspace('exotic'), 'exotic')

    def test_to_str(self):
        self.assertEqual(safe_colorspace_to_str(ColorSpace.bt709), 'bt709')
        self.assertEqual(safe_colorspace_to_str('exotic'), 'exotic')