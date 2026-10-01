"""
Unit tests for BlisterGridDetector.
"""

import unittest
import numpy as np
from pharmacount.config import PackConfig
from pharmacount.grid_detector import BlisterGridDetector


class TestBlisterGridDetector(unittest.TestCase):

    def setUp(self):
        self.config = PackConfig(expected_rows=2, expected_cols=5)
        self.detector = BlisterGridDetector(self.config)
        self.test_img = np.zeros((300, 600, 3), dtype=np.uint8)

    def test_extract_pockets_count(self):
        pockets = self.detector.extract_pockets(self.test_img, pack_box=(0, 0, 600, 300))
        self.assertEqual(len(pockets), 10)
        self.assertEqual(pockets[0].row, 1)
        self.assertEqual(pockets[0].col, 1)
        self.assertEqual(pockets[-1].row, 2)
        self.assertEqual(pockets[-1].col, 5)

    def test_pockets_within_bounds(self):
        pockets = self.detector.extract_pockets(self.test_img, pack_box=(0, 0, 600, 300))
        h, w = self.test_img.shape[:2]
        for p in pockets:
            x, y, pw, ph = p.bbox
            self.assertGreaterEqual(x, 0)
            self.assertGreaterEqual(y, 0)
            self.assertLessEqual(x + pw, w)
            self.assertLessEqual(y + ph, h)


if __name__ == "__main__":
    unittest.main()
