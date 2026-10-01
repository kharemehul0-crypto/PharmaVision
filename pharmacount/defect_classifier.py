"""
Defect Classification and Pack Decision Logic Module.
Combines geometric descriptors, occupancy indicators, and colorimetric metrics
to categorize each pocket into NORMAL, MISSING, CHIPPED, or DISCOLORED.
"""

from typing import List, Optional
import time
import numpy as np
from .config import PackConfig, TabletStatus, PocketMetric, InspectionResult
from .grid_detector import BlisterGridDetector
from .contour_analyzer import TabletContourAnalyzer
from .color_inspector import TabletColorInspector


class TabletDefectClassifier:
    """
    Main inspection pipeline classifier. Evaluates full blister packs
    by coordinating pocket segmentation, contour analysis, and color grading.
    """

    def __init__(self, config: Optional[PackConfig] = None):
        self.config = config or PackConfig()
        self.grid_detector = BlisterGridDetector(self.config)
        self.contour_analyzer = TabletContourAnalyzer(self.config)
        self.color_inspector = TabletColorInspector(self.config)

    def inspect_pack(self, bgr_image: np.ndarray, image_name: str = "sample") -> InspectionResult:
        """
        Executes end-to-end inspection on a blister pack image.
        
        Args:
            bgr_image: Original input BGR image.
            image_name: Identifier for reporting.
            
        Returns:
            InspectionResult object containing aggregated metrics and pass/fail state.
        """
        start_time = time.perf_counter()

        # Step 1: Detect grid and isolate pocket ROIs
        pack_box = self.grid_detector.find_pack_boundary(bgr_image)
        pockets = self.grid_detector.extract_pockets(bgr_image, pack_box)

        # Step 2: First pass - extract contours & raw metrics for all pockets
        raw_contours = []
        raw_areas = []

        for p in pockets:
            pocket_roi = self.grid_detector.crop_pocket_roi(bgr_image, p.bbox)
            contour, mask = self.contour_analyzer.segment_tablet_contour(pocket_roi)
            shape_metrics = self.contour_analyzer.compute_shape_metrics(contour, pocket_roi.shape[:2])
            
            raw_contours.append((contour, pocket_roi))
            if shape_metrics["area"] > 0:
                raw_areas.append(shape_metrics["area"])
            
            p.area = shape_metrics["area"]
            p.perimeter = shape_metrics["perimeter"]
            p.circularity = shape_metrics["circularity"]
            p.solidity = shape_metrics["solidity"]

        # Step 3: Determine expected tablet area baseline
        # Use median of candidate tablet areas; fallback to 35% of pocket area if all empty
        if len(raw_areas) >= 2:
            expected_tablet_area = float(np.median(raw_areas))
        elif len(raw_areas) == 1:
            expected_tablet_area = raw_areas[0]
        else:
            first_w, first_h = pockets[0].bbox[2], pockets[0].bbox[3]
            expected_tablet_area = (first_w * first_h) * 0.35

        # Step 4: Second pass - evaluate and classify each pocket
        missing_count = 0
        chipped_count = 0
        discolored_count = 0
        tablets_present = 0

        for i, p in enumerate(pockets):
            contour, pocket_roi = raw_contours[i]
            
            # Check empty / missing tablet
            area_ratio = p.area / (expected_tablet_area + 1e-5)

            if contour is None or area_ratio < self.config.empty_pocket_area_ratio:
                p.status = TabletStatus.MISSING
                p.defect_reason = f"No tablet detected (area ratio: {area_ratio:.2f})"
                missing_count += 1
                continue

            # Tablet is present
            tablets_present += 1

            # Extract color information
            mean_bgr, delta_e = self.color_inspector.extract_tablet_color(pocket_roi, contour)
            p.mean_bgr = mean_bgr
            p.delta_e = delta_e

            # Check geometric defects: chipped or broken
            is_under_area = area_ratio < self.config.min_area_ratio
            is_low_circ = p.circularity < self.config.min_circularity
            is_low_solidity = p.solidity < self.config.min_solidity

            if is_under_area or is_low_circ or is_low_solidity:
                p.status = TabletStatus.CHIPPED
                reasons = []
                if is_under_area:
                    reasons.append(f"Area deficit ({area_ratio*100:.1f}%)")
                if is_low_circ:
                    reasons.append(f"Low circularity ({p.circularity:.2f})")
                if is_low_solidity:
                    reasons.append(f"Low solidity ({p.solidity:.2f})")
                p.defect_reason = "; ".join(reasons)
                chipped_count += 1
                continue

            # Check colorimetric defect: contamination or discoloration
            if not self.color_inspector.is_color_compliant(delta_e):
                p.status = TabletStatus.DISCOLORED
                p.defect_reason = f"Color deviation (Delta-E: {delta_e:.1f} > threshold {self.config.max_delta_e})"
                discolored_count += 1
                continue

            # If all checks pass, tablet is normal
            p.status = TabletStatus.NORMAL
            p.defect_reason = "Compliant"

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        total_defects = missing_count + chipped_count + discolored_count
        is_passed = (total_defects == 0) and (tablets_present == len(pockets))

        return InspectionResult(
            image_name=image_name,
            is_passed=is_passed,
            total_pockets=len(pockets),
            tablets_present=tablets_present,
            missing_count=missing_count,
            chipped_count=chipped_count,
            discolored_count=discolored_count,
            processing_time_ms=elapsed_ms,
            pocket_metrics=pockets
        )
