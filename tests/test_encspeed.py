# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

import unittest

from vtcff._hevc_encspeed import VcPreset


class TestEncSpeed(unittest.TestCase):
    def test_faster(self):
        self.assertEqual(
            VcPreset.faster(VcPreset.n10_placebo),
            VcPreset.n9_veryslow)
        self.assertEqual(
            VcPreset.faster(VcPreset.n2_superfast),
            VcPreset.n1_ultrafast)
        with self.assertRaises(IndexError):
            VcPreset.faster(VcPreset.n1_ultrafast)
        with self.assertRaises(ValueError):
            VcPreset.faster("lbauda")
