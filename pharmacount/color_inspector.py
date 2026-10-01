"""
Tablet Colorimetric Inspection Module.
Performs color consistency checks in CIE L*a*b* space using Euclidean Delta-E.
Detects foreign tablets, chemical degradation, or batch discoloration.
"""

from typing import Tuple, Optional
import math
import cv2
import numpy as np
from .config import PackConfig


class TabletColorInspector:
    """
    Evaluates color uniformity and perceptual color difference (Delta-E)
    against the expected golden batch tablet reference color.
    """

    def __init__(self, config: Optional[PackConfig] = None):
        self.config = config or PackConfig()
        
        # Convert expected reference BGR into CIE L*a*b*
        ref_bgr_pixel = np.uint8([[list(self.config.reference_color_bgr)]])
        ref_lab_pixel = cv2.cvtColor(ref_bgr_pixel, cv2.COLOR_BGR2LAB)
        self.reference_lab = ref_lab_pixel[0, 0].astype(np.float32)

    def extract_tablet_color(self, pocket_bgr: np.ndarray, contour: Optional[np.ndarray]) -> Tuple[Tuple[float, float, float], float]:
        """
        Calculates mean BGR color and Delta-E distance from reference tablet.
        
        Args:
            pocket_bgr: Pocket sub-image.
            contour: Tablet contour. If None, returns default values.
            
        Returns:
            Tuple of (mean_bgr, delta_e).
        """
        if contour is None or pocket_bgr is None or pocket_bgr.size == 0:
            return (0.0, 0.0, 0.0), 999.0

        # Create mask restricted to the tablet contour interior
        h, w = pocket_bgr.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.drawContours(mask, [contour], -1, 255, thickness=-1)

        # Erode mask slightly (by 2 pixels) to prevent metallic border bleeding into color sample
        erode_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask_eroded = cv2.erode(mask, erode_kernel, iterations=1)
        if cv2.countNonZero(mask_eroded) > 20:
            sample_mask = mask_eroded
        else:
            sample_mask = mask

        # Mean BGR
        mean_bgr = cv2.mean(pocket_bgr, mask=sample_mask)[:3]

        # Convert pocket image to CIE L*a*b*
        pocket_lab = cv2.cvtColor(pocket_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
        
        # Calculate mean L*a*b* under sample mask
        indices = np.where(sample_mask > 0)
        if len(indices[0]) == 0:
            return mean_bgr, 999.0

        sample_lab_values = pocket_lab[indices]
        mean_lab = np.mean(sample_lab_values, axis=0)

        # Euclidean Delta-E (CIE 1976 formula)
        # Delta E = sqrt((L1 - L2)^2 + (a1 - a2)^2 + (b1 - b2)^2)
        delta_l = mean_lab[0] - self.reference_lab[0]
        delta_a = mean_lab[1] - self.reference_lab[1]
        delta_b = mean_lab[2] - self.reference_lab[2]
        delta_e = math.sqrt(delta_l**2 + delta_a**2 + delta_b**2)

        return mean_bgr, delta_e

    def is_color_compliant(self, delta_e: float) -> bool:
        """Determines whether Delta-E is within acceptable production tolerance."""
        return delta_e <= self.config.max_delta_e
