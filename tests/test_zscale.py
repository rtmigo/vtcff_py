# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

import unittest

from vtcff._filter_zscale import ZscaleFilter


class TestZscaleCommand(unittest.TestCase):
    def test_empty(self):
        z = ZscaleFilter()
        self.assertEqual(str(z), '')

    def test_full_to_limited(self):
        z = ZscaleFilter()
        z.src_range_full = True
        z.dst_range_full = False
        self.assertEqual(str(z),
                         'zscale=rangein=full:range=limited:dither=error_diffusion')

    def test_709_plus(self):
        z = ZscaleFilter()
        # z.range_full_to_limited()
        z.dst_matrix = '709'
        self.assertEqual(str(z), 'zscale=matrix=709:dither=error_diffusion')
