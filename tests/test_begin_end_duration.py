import unittest

from vtcff._time_span import BeginEndDuration


class TestBed(unittest.TestCase):
    def test_default(self):
        bed = BeginEndDuration()
        self.assertEqual(bed.begin, 0)
        self.assertIsNone(bed.end)
        self.assertIsNone(bed.duration)

    def test_begin_end_to_duration(self):
        bed = BeginEndDuration()
        bed.begin = 1
        bed.end = 5
        self.assertEqual(bed.begin, 1)
        self.assertEqual(bed.end, 5)
        self.assertEqual(bed.duration, 4)

    def test_end_only(self):
        bed = BeginEndDuration()
        bed.end = 5
        self.assertEqual(bed.begin, 0)
        self.assertEqual(bed.end, 5)
        self.assertEqual(bed.duration, 5)
