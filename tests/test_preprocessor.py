"""
Unit tests for ImagePreprocessor.
"""

import unittest
import numpy as np
import cv2
from pharmacount.config import PackConfig
from pharmacount.preprocessor import ImagePreprocessor


class TestImagePreprocessor(unittest.TestCase):

    def setUp(self):
        self.config = PackConfig()
        self.preprocessor = ImagePreprocessor(self.config)
        # Create a synthetic 100x100 BGR test patch
        self.sample_bgr = np.full((100, 100, 3), 128, dtype=np.uint8)

    def test_denoise_bilateral_preserves_shape(self):
        denoised = self.preprocessor.denoise_bilateral(self.sample_bgr)
        self.assertEqual(denoised.shape, self.sample_bgr.shape)
        self.assertEqual(denoised.dtype, np.uint8)

    def test_enhance_contrast_clahe(self):
        gray = cv2.cvtColor(self.sample_bgr, cv2.COLOR_BGR2GRAY)
        clahe_out = self.preprocessor.enhance_contrast_clahe(gray)
        self.assertEqual(clahe_out.shape, gray.shape)

    def test_convert_color_spaces(self):
        gray, hsv, lab = self.preprocessor.convert_color_spaces(self.sample_bgr)
        self.assertEqual(gray.shape, (100, 100))
        self.assertEqual(hsv.shape, (100, 100, 3))
        self.assertEqual(lab.shape, (100, 100, 3))


if __name__ == "__main__":
    unittest.main()
