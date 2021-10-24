# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

import unittest

from vtcff._encspeed import Speed


class TestEncSpeed(unittest.TestCase):
    def test_faster(self):
        self.assertEqual(
            Speed.faster(Speed.n10_placebo),
            Speed.n9_veryslow)
        self.assertEqual(
            Speed.faster(Speed.n2_superfast),
            Speed.n1_ultrafast)
        with self.assertRaises(IndexError):
            Speed.faster(Speed.n1_ultrafast)
        with self.assertRaises(ValueError):
            Speed.faster("lbauda")