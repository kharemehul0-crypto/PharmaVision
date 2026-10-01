"""
Tablet Shape and Geometric Contour Analysis Module.
Extracts tablet boundaries from pocket ROIs and computes mathematical
descriptors: area, circularity (roundness), solidity, and convexity defects.
"""

from typing import Tuple, Optional, Dict, Any
import math
import cv2
import numpy as np
from .config import PackConfig


class TabletContourAnalyzer:
    """
    Analyzes geometric contours of tablets inside pocket ROIs.
    Distinguishes intact circular/oval tablets from chipped or fragmented pills.
    """

    def __init__(self, config: Optional[PackConfig] = None):
        self.config = config or PackConfig()

    def segment_tablet_contour(self, pocket_bgr: np.ndarray) -> Tuple[Optional[np.ndarray], np.ndarray]:
        """
        Segments the primary tablet mass from the pocket background.
        
        Args:
            pocket_bgr: Cropped BGR image of a single pocket.
            
        Returns:
            Tuple of (primary_contour, binary_mask).
            If no tablet is present, primary_contour is None.
        """
        if pocket_bgr is None or pocket_bgr.size == 0:
            return None, np.zeros((10, 10), dtype=np.uint8)

        gray = cv2.cvtColor(pocket_bgr, cv2.COLOR_BGR2GRAY)
        
        # Apply median blur to reduce salt-and-pepper foil reflections
        blurred = cv2.medianBlur(gray, 5)
        
        # Otsu's thresholding
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Test if tablet is brighter than pocket background (typical in blister packs)
        # If tablet is inverted, flip threshold
        h, w = gray.shape
        center_roi = thresh[h//4:3*h//4, w//4:3*w//4]
        border_mean = np.mean([
            np.mean(thresh[0:3, :]),
            np.mean(thresh[-3:, :]),
            np.mean(thresh[:, 0:3]),
            np.mean(thresh[:, -3:])
        ])
        
        # If the outer border is white and center is dark, invert so tablet is 255
        if border_mean > 127 and np.mean(center_roi) < border_mean:
            thresh = cv2.bitwise_not(thresh)

        # Morphological opening using elliptical structuring element to detach foil seams
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask_clean = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, kernel, iterations=1)

        contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None, mask_clean

        # Filter contours by minimum size and proximity to pocket center
        pocket_area = h * w
        min_valid_area = pocket_area * 0.05  # At least 5% of pocket

        best_contour = None
        max_area = 0.0
        center_x, center_y = w / 2.0, h / 2.0

        for c in contours:
            area = cv2.contourArea(c)
            if area > min_valid_area:
                m = cv2.moments(c)
                if m["m00"] > 0:
                    cx = m["m10"] / m["m00"]
                    cy = m["m01"] / m["m00"]
                    dist_to_center = math.hypot(cx - center_x, cy - center_y)
                    if dist_to_center < (max(w, h) * 0.40):
                        if area > max_area:
                            max_area = area
                            best_contour = c

        # Verify that candidate contour has actual tablet contrast (not empty foil recess)
        if best_contour is not None:
            c_mask = np.zeros(gray.shape, dtype=np.uint8)
            cv2.drawContours(c_mask, [best_contour], -1, 255, -1)
            mean_intensity = cv2.mean(gray, mask=c_mask)[0]
            # In metallic blister packs, empty cavities have mean gray < 130 without color
            hsv = cv2.cvtColor(pocket_bgr, cv2.COLOR_BGR2HSV)
            mean_sat = cv2.mean(hsv[:, :, 1], mask=c_mask)[0]
            if mean_intensity < 140 and mean_sat < 35:
                # This is an empty foil pocket recess
                return None, mask_clean

        return best_contour, mask_clean

    def compute_shape_metrics(self, contour: Optional[np.ndarray], pocket_shape: Tuple[int, int]) -> Dict[str, float]:
        """
        Computes geometric invariant descriptors for a tablet contour:
        - Area: total pixel count inside contour
        - Perimeter: arc length
        - Circularity (Isoperimetric Quotient): 4 * pi * Area / Perimeter^2
        - Solidity: Area / Convex_Hull_Area
        
        Returns:
            Dict containing area, perimeter, circularity, and solidity.
        """
        if contour is None:
            return {
                "area": 0.0,
                "perimeter": 0.0,
                "circularity": 0.0,
                "solidity": 0.0
            }

        area = float(cv2.contourArea(contour))
        perimeter = float(cv2.arcLength(contour, closed=True))

        if perimeter <= 0 or area <= 0:
            return {
                "area": area,
                "perimeter": perimeter,
                "circularity": 0.0,
                "solidity": 0.0
            }

        # Circularity calculation
        circularity = (4.0 * math.pi * area) / (perimeter * perimeter)
        circularity = min(1.0, max(0.0, circularity))

        # Convex Hull and Solidity
        hull = cv2.convexHull(contour)
        hull_area = float(cv2.contourArea(hull))
        solidity = (area / hull_area) if hull_area > 0 else 0.0
        solidity = min(1.0, max(0.0, solidity))

        return {
            "area": area,
            "perimeter": perimeter,
            "circularity": circularity,
            "solidity": solidity
        }
