"""
Unit tests for TabletContourAnalyzer.
"""

import unittest
import numpy as np
import cv2
from pharmacount.config import PackConfig
from pharmacount.contour_analyzer import TabletContourAnalyzer


class TestTabletContourAnalyzer(unittest.TestCase):

    def setUp(self):
        self.config = PackConfig()
        self.analyzer = TabletContourAnalyzer(self.config)

    def test_circular_shape_metrics(self):
        # Draw a solid white circle on black background
        img = np.zeros((100, 100), dtype=np.uint8)
        cv2.circle(img, (50, 50), 30, 255, -1)
        
        contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        metrics = self.analyzer.compute_shape_metrics(contours[0], (100, 100))
        
        # A circle has circularity close to 1.0 (approx > 0.85 due to discrete pixel grid)
        self.assertGreater(metrics["circularity"], 0.80)
        # A convex shape has solidity close to 1.0
        self.assertGreater(metrics["solidity"], 0.95)

    def test_none_contour_returns_zero(self):
        metrics = self.analyzer.compute_shape_metrics(None, (100, 100))
        self.assertEqual(metrics["area"], 0.0)
        self.assertEqual(metrics["circularity"], 0.0)
        self.assertEqual(metrics["solidity"], 0.0)


if __name__ == "__main__":
    unittest.main()
