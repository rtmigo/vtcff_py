# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

import unittest

from tests.common import find_item_after, create_test_cmd
from vtcff import FfmpegCommand, crop_and_scale


class TestCropAndScale(unittest.TestCase):


    def test(self):
        cmd = create_test_cmd(zscale=True)
        crop_and_scale(cmd,
                       src_width=4096,
                       src_height=2160,
                       dst_width=1920,
                       dst_height=1080)

        vf: str = find_item_after(cmd, '-vf')

        self.assertIn('crop=3840:2160:128:0', vf)
        self.assertIn(':w=-2:h=1080', vf)
        # убедимся, что кроп делаем сначала, а скейлинг потом
        self.assertLess(vf.index('crop='), vf.index('zscale='))

#        self.fail(vf)
 #       pass
