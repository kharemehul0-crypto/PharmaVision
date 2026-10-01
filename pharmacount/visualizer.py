"""
Inspection Visualization and Annotation Overlay Module.
Renders high-visibility bounding boxes, status color codes, HUD banners,
and measurement metrics directly on the inspection image.
"""

from typing import Tuple
import cv2
import numpy as np
from .config import TabletStatus, InspectionResult, PocketMetric


class InspectionVisualizer:
    """
    Renders visual inspection overlays and diagnostic HUD elements.
    """

    COLOR_MAP = {
        TabletStatus.NORMAL: (46, 204, 113),       # Emerald Green (BGR)
        TabletStatus.MISSING: (41, 41, 231),       # Vivid Red
        TabletStatus.CHIPPED: (0, 140, 255),       # Deep Orange
        TabletStatus.DISCOLORED: (186, 85, 211),   # Orchid / Violet
    }

    def render_overlay(self, original_bgr: np.ndarray, result: InspectionResult) -> np.ndarray:
        """
        Draws pocket bounding boxes, index labels, and an industrial HUD banner.
        
        Args:
            original_bgr: Original input BGR image.
            result: InspectionResult containing evaluated metrics.
            
        Returns:
            np.ndarray: Annotated BGR image.
        """
        vis_image = original_bgr.copy()
        h_img, w_img = vis_image.shape[:2]

        # Draw each pocket cell
        for p in result.pocket_metrics:
            self._draw_pocket(vis_image, p)

        # Draw top HUD banner
        vis_image = self._draw_hud_banner(vis_image, result)

        return vis_image

    def _draw_pocket(self, img: np.ndarray, p: PocketMetric) -> None:
        """Draws individual pocket boundary and status tag."""
        x, y, w, h = p.bbox
        color = self.COLOR_MAP.get(p.status, (200, 200, 200))

        # Main pocket border
        thickness = 2 if p.status == TabletStatus.NORMAL else 3
        cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)

        # If missing, draw an X inside the pocket
        if p.status == TabletStatus.MISSING:
            cv2.line(img, (x + 8, y + 8), (x + w - 8, y + h - 8), color, 2)
            cv2.line(img, (x + w - 8, y + 8), (x + 8, y + h - 8), color, 2)

        # Pocket label badge
        label = f"#{p.index} {p.status.value}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.42
        font_thickness = 1
        (txt_w, txt_h), baseline = cv2.getTextSize(label, font, font_scale, font_thickness)

        badge_y1 = max(0, y - txt_h - 6)
        badge_y2 = y
        badge_x1 = x
        badge_x2 = x + txt_w + 6

        cv2.rectangle(img, (badge_x1, badge_y1), (badge_x2, badge_y2), color, -1)
        text_color = (0, 0, 0) if p.status == TabletStatus.NORMAL or p.status == TabletStatus.CHIPPED else (255, 255, 255)
        cv2.putText(img, label, (badge_x1 + 3, badge_y2 - 3), font, font_scale, text_color, font_thickness, cv2.LINE_AA)

        # Optional detail metric below pocket
        if p.status != TabletStatus.MISSING:
            metric_text = f"C:{p.circularity:.2f} S:{p.solidity:.2f}"
            cv2.putText(img, metric_text, (x + 2, y + h - 4), font, 0.35, (240, 240, 240), 1, cv2.LINE_AA)

    def _draw_hud_banner(self, img: np.ndarray, result: InspectionResult) -> np.ndarray:
        """Renders header bar with batch status, counts, and latency."""
        h_img, w_img = img.shape[:2]
        banner_height = 65

        # Create banner canvas
        banner = np.zeros((banner_height, w_img, 3), dtype=np.uint8)
        banner[:] = (30, 30, 30)  # Dark slate background

        # Status badge (PASS / REJECT)
        status_text = "PASS" if result.is_passed else "REJECT"
        status_color = (46, 204, 113) if result.is_passed else (41, 41, 231)
        
        cv2.rectangle(banner, (12, 10), (140, 55), status_color, -1)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(banner, status_text, (24, 43), font, 0.9, (255, 255, 255), 2, cv2.LINE_AA)

        # Text statistics
        font_sub = cv2.FONT_HERSHEY_SIMPLEX
        line1 = f"TABLETS: {result.tablets_present}/{result.total_pockets} ({result.fill_rate_percent:.0f}%) | DEFECTS: {result.total_defects}"
        line2 = f"Missing: {result.missing_count} | Chipped: {result.chipped_count} | Discolored: {result.discolored_count} | Latency: {result.processing_time_ms:.1f}ms"
        
        cv2.putText(banner, line1, (160, 28), font_sub, 0.52, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(banner, line2, (160, 50), font_sub, 0.44, (180, 180, 180), 1, cv2.LINE_AA)

        # Concatenate banner on top of image
        combined = np.vstack([banner, img])
        return combined
