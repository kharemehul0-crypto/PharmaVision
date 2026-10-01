"""
PharmaCount-CV: Vision-Based Pharmaceutical Blister Pack & Tablet Integrity Inspector
Course: Computer Vision
"""

__version__ = "1.0.0"
__author__ = "Computer Vision Project Submission"

from .config import PackConfig, TabletStatus, InspectionResult, PocketMetric
from .preprocessor import ImagePreprocessor
from .grid_detector import BlisterGridDetector
from .contour_analyzer import TabletContourAnalyzer
from .color_inspector import TabletColorInspector
from .defect_classifier import TabletDefectClassifier
from .visualizer import InspectionVisualizer
from .report_engine import ReportEngine

__all__ = [
    "PackConfig",
    "TabletStatus",
    "InspectionResult",
    "PocketMetric",
    "ImagePreprocessor",
    "BlisterGridDetector",
    "TabletContourAnalyzer",
    "TabletColorInspector",
    "TabletDefectClassifier",
    "InspectionVisualizer",
    "ReportEngine",
]
