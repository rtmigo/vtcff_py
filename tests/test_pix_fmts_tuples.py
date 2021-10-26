import unittest

from vtcff._pix_formats_reader import _pix_fmts_tuples, pix_format_spec


class TestPixFmts(unittest.TestCase):
    def test_read_tuples(self):
        lst = _pix_fmts_tuples()
        self.assertGreater(len(lst), 5)
        z = next(x for x in lst if x.name == "yuv422p10le")
        self.assertEqual(z.bits_per_pixel, 20)
        self.assertEqual(z.nb_components, 3)
        self.assertEqual(z.flags, 'IO...')

    def test_get_by_name(self):
        z = pix_format_spec('yuva444p10le')
        self.assertEqual(z.name, 'yuva444p10le')
        self.assertEqual(z.bits_per_pixel, 40)

        with self.assertRaises(KeyError):
            pix_format_spec('abcd')
