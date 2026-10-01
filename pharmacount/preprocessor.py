"""
Image Preprocessing and Color Space Normalization Module.
Applies bilateral filtering and CLAHE to handle metallic foil specular glare
and uneven industrial lighting conditions.
"""

import os
from typing import Tuple, Optional
import cv2
import numpy as np
from .config import PackConfig


class ImagePreprocessor:
    """
    Handles image ingestion, noise reduction, illumination correction,
    and multi-color-space transformations.
    """

    def __init__(self, config: Optional[PackConfig] = None):
        self.config = config or PackConfig()
        self.clahe = cv2.createCLAHE(
            clipLimit=self.config.clahe_clip_limit,
            tileGridSize=self.config.clahe_tile_grid_size
        )

    def load_image(self, image_path: str) -> np.ndarray:
        """
        Loads an image from disk with validation.
        
        Args:
            image_path: Absolute or relative filesystem path.
            
        Returns:
            np.ndarray: BGR image array.
            
        Raises:
            FileNotFoundError: If path does not exist.
            ValueError: If file cannot be decoded as an image.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Input image not found: {image_path}")

        image = cv2.imread(image_path)
        if image is None or image.size == 0:
            raise ValueError(f"Failed to decode image from path: {image_path}")

        return image

    def denoise_bilateral(self, bgr_image: np.ndarray) -> np.ndarray:
        """
        Applies edge-preserving bilateral filtering to suppress foil grain
        while maintaining crisp tablet boundaries.
        """
        return cv2.bilateralFilter(
            bgr_image,
            d=self.config.bilateral_d,
            sigmaColor=self.config.bilateral_sigma_color,
            sigmaSpace=self.config.bilateral_sigma_space
        )

    def enhance_contrast_clahe(self, gray_image: np.ndarray) -> np.ndarray:
        """
        Applies Contrast-Limited Adaptive Histogram Equalization (CLAHE)
        to normalize uneven illumination and shadow gradients across blister packs.
        """
        return self.clahe.apply(gray_image)

    def convert_color_spaces(self, bgr_image: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Converts BGR image into Grayscale, HSV, and CIE L*a*b* representations.
        
        Returns:
            Tuple of (gray, hsv, lab) numpy arrays.
        """
        gray = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2LAB)
        return gray, hsv, lab

    def segment_pack_mask(self, bgr_image: np.ndarray) -> np.ndarray:
        """
        Generates a binary mask isolating the overall blister pack from the background.
        Uses Otsu's thresholding followed by morphological closing.
        """
        gray = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)
        
        # Otsu thresholding
        _, mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # If background is lighter than the blister pack border, invert
        border_mean = np.mean([
            np.mean(mask[0:10, :]),
            np.mean(mask[-10:, :]),
            np.mean(mask[:, 0:10]),
            np.mean(mask[:, -10:])
        ])
        if border_mean > 127:
            mask = cv2.bitwise_not(mask)

        # Morphological closing to seal internal pocket gaps
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        mask_closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        return mask_closed
