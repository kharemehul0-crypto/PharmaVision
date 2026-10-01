"""
Blister Pack Localization and Grid Extraction Module.
Identifies the blister pack boundary and partitions the packaging area
into discrete pocket cells corresponding to individual tablet cavities.
"""

from typing import List, Tuple, Optional
import cv2
import numpy as np
from .config import PackConfig, PocketMetric


class BlisterGridDetector:
    """
    Detects the blister pack card region and segments it into an R x C grid
    of individual tablet pocket Regions of Interest (ROIs).
    """

    def __init__(self, config: Optional[PackConfig] = None):
        self.config = config or PackConfig()

    def find_pack_boundary(self, bgr_image: np.ndarray) -> Tuple[int, int, int, int]:
        """
        Locates the outermost bounding box of the blister card.
        If no distinct outer contour is detected, falls back to the full image boundary.
        
        Returns:
            Tuple of (x, y, w, h)
        """
        h_img, w_img = bgr_image.shape[:2]
        gray = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 30, 120)
        
        # Dilate edges to bridge gaps along card edges
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        closed_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(closed_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        best_box = (0, 0, w_img, h_img)
        max_area = 0.0
        min_card_area = (w_img * h_img) * 0.25  # Card must occupy at least 25% of image

        for c in contours:
            area = cv2.contourArea(c)
            if area > max_area and area >= min_card_area:
                x, y, w, h = cv2.boundingRect(c)
                # Avoid selecting the exact edge of the entire image if it's a border artifact
                if w < w_img * 0.98 or h < h_img * 0.98:
                    max_area = area
                    best_box = (x, y, w, h)

        return best_box

    def extract_pockets(self, bgr_image: np.ndarray, pack_box: Optional[Tuple[int, int, int, int]] = None) -> List[PocketMetric]:
        """
        Subdivides the blister card region into expected grid cells (rows x cols).
        
        Returns:
            List of PocketMetric objects with initialized spatial bounding boxes.
        """
        if pack_box is None:
            pack_box = self.find_pack_boundary(bgr_image)

        px, py, pw, ph = pack_box
        rows = self.config.expected_rows
        cols = self.config.expected_cols

        # Compute internal active area by discounting packaging margins
        margin_x = int(pw * self.config.margin_x_ratio)
        margin_y = int(ph * self.config.margin_y_ratio)

        active_x = px + margin_x
        active_y = py + margin_y
        active_w = pw - (2 * margin_x)
        active_h = ph - (2 * margin_y)

        cell_w = active_w / cols
        cell_h = active_h / rows

        pockets: List[PocketMetric] = []
        idx = 1

        for r in range(rows):
            for c in range(cols):
                # Calculate pocket ROI coordinates
                cell_x1 = int(active_x + (c * cell_w))
                cell_y1 = int(active_y + (r * cell_h))
                cell_x2 = int(active_x + ((c + 1) * cell_w))
                cell_y2 = int(active_y + ((r + 1) * cell_h))

                # Add inner padding so neighboring pocket borders do not bleed in
                pad_x = int(cell_w * 0.08)
                pad_y = int(cell_h * 0.08)

                x = max(0, cell_x1 + pad_x)
                y = max(0, cell_y1 + pad_y)
                w = max(10, (cell_x2 - cell_x1) - (2 * pad_x))
                h = max(10, (cell_y2 - cell_y1) - (2 * pad_y))

                # Constrain within image bounds
                img_h, img_w = bgr_image.shape[:2]
                w = min(w, img_w - x)
                h = min(h, img_h - y)

                pockets.append(PocketMetric(
                    index=idx,
                    row=r + 1,
                    col=c + 1,
                    bbox=(x, y, w, h)
                ))
                idx += 1

        return pockets

    def crop_pocket_roi(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
        """Helper to crop pocket sub-image."""
        x, y, w, h = bbox
        return image[y:y+h, x:x+w]
