"""
Configuration profiles and data structures for PharmaCount-CV.
Defines tolerance thresholds for geometry, morphology, and color inspection.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple, List, Optional
import json


class TabletStatus(str, Enum):
    """Enumeration of possible tablet health states."""
    NORMAL = "NORMAL"
    MISSING = "MISSING"
    CHIPPED = "CHIPPED"
    DISCOLORED = "DISCOLORED"


@dataclass
class PackConfig:
    """
    Configuration parameters for blister pack geometry and defect detection thresholds.
    """
    # Grid layout expectations
    expected_rows: int = 2
    expected_cols: int = 5
    
    # Preprocessing parameters
    bilateral_d: int = 9
    bilateral_sigma_color: float = 75.0
    bilateral_sigma_space: float = 75.0
    clahe_clip_limit: float = 2.0
    clahe_tile_grid_size: Tuple[int, int] = (8, 8)
    
    # Area thresholds relative to expected tablet area (in pixels)
    # If tablet contour area is below min_area_ratio, it is considered missing or broken
    min_area_ratio: float = 0.65
    max_area_ratio: float = 1.35
    empty_pocket_area_ratio: float = 0.20
    
    # Shape fidelity thresholds
    # Circularity = 4 * pi * Area / (Perimeter^2). Perfect circle = 1.0.
    min_circularity: float = 0.76
    
    # Solidity = Area / Convex_Hull_Area. Chipped tablets show significant indentation.
    min_solidity: float = 0.90
    
    # Color inspection thresholds (CIE L*a*b* space delta-E)
    # Expected reference color in BGR format: default is pure white/light grey tablet
    reference_color_bgr: Tuple[int, int, int] = (235, 235, 235)
    max_delta_e: float = 28.0
    
    # Blister pack margins (fraction of pack size to trim packaging borders)
    margin_x_ratio: float = 0.05
    margin_y_ratio: float = 0.05

    def to_dict(self) -> dict:
        """Serialize configuration to dictionary."""
        return {
            "expected_rows": self.expected_rows,
            "expected_cols": self.expected_cols,
            "expected_total": self.expected_rows * self.expected_cols,
            "min_area_ratio": self.min_area_ratio,
            "max_area_ratio": self.max_area_ratio,
            "empty_pocket_area_ratio": self.empty_pocket_area_ratio,
            "min_circularity": self.min_circularity,
            "min_solidity": self.min_solidity,
            "reference_color_bgr": list(self.reference_color_bgr),
            "max_delta_e": self.max_delta_e,
        }

    @classmethod
    def from_file(cls, json_path: str) -> "PackConfig":
        """Load configuration from a JSON file."""
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        cfg = cls()
        for k, v in data.items():
            if hasattr(cfg, k):
                if k == "reference_color_bgr" and isinstance(v, list):
                    v = tuple(v)
                setattr(cfg, k, v)
        return cfg


@dataclass
class PocketMetric:
    """Stores quantitative measurements for an individual blister pocket."""
    index: int
    row: int
    col: int
    bbox: Tuple[int, int, int, int]  # (x, y, w, h)
    status: TabletStatus = TabletStatus.MISSING
    area: float = 0.0
    perimeter: float = 0.0
    circularity: float = 0.0
    solidity: float = 0.0
    delta_e: float = 0.0
    mean_bgr: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    defect_reason: str = ""

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "grid_position": {"row": self.row, "col": self.col},
            "bounding_box": {"x": self.bbox[0], "y": self.bbox[1], "w": self.bbox[2], "h": self.bbox[3]},
            "status": self.status.value,
            "area_px": round(self.area, 2),
            "perimeter_px": round(self.perimeter, 2),
            "circularity": round(self.circularity, 4),
            "solidity": round(self.solidity, 4),
            "color_delta_e": round(self.delta_e, 2),
            "mean_bgr": [round(c, 1) for c in self.mean_bgr],
            "defect_reason": self.defect_reason
        }


@dataclass
class InspectionResult:
    """Aggregated inspection report for a full blister pack."""
    image_name: str
    is_passed: bool
    total_pockets: int
    tablets_present: int
    missing_count: int
    chipped_count: int
    discolored_count: int
    processing_time_ms: float
    pocket_metrics: List[PocketMetric] = field(default_factory=list)

    @property
    def total_defects(self) -> int:
        return self.missing_count + self.chipped_count + self.discolored_count

    @property
    def fill_rate_percent(self) -> float:
        if self.total_pockets == 0:
            return 0.0
        return (self.tablets_present / self.total_pockets) * 100.0

    def to_dict(self) -> dict:
        return {
            "image_name": self.image_name,
            "overall_status": "PASS" if self.is_passed else "REJECT",
            "summary": {
                "total_pockets": self.total_pockets,
                "tablets_present": self.tablets_present,
                "fill_rate_percent": round(self.fill_rate_percent, 2),
                "total_defects": self.total_defects,
                "missing_count": self.missing_count,
                "chipped_count": self.chipped_count,
                "discolored_count": self.discolored_count,
                "processing_time_ms": round(self.processing_time_ms, 2)
            },
            "pockets": [p.to_dict() for p in self.pocket_metrics]
        }
