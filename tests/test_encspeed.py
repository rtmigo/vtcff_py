# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

import unittest

from vtcff._codec_avc_preset import VcPreset


class TestEncSpeed(unittest.TestCase):
    def test_faster(self):
        self.assertEqual(
            VcPreset.faster(VcPreset.N10_PLACEBO),
            VcPreset.N9_VERYSLOW)
        self.assertEqual(
            VcPreset.faster(VcPreset.N2_SUPERFAST),
            VcPreset.N1_ULTRAFAST)
        with self.assertRaises(IndexError):
            VcPreset.faster(VcPreset.N1_ULTRAFAST)
        with self.assertRaises(ValueError):
            VcPreset.faster("lbauda")
