"""
Unit tests for TabletDefectClassifier.
"""

import unittest
import numpy as np
from pharmacount.config import PackConfig, TabletStatus
from pharmacount.defect_classifier import TabletDefectClassifier
from dataset.generate_synthetic_data import create_blister_background, draw_pocket_cavity, draw_tablet


class TestTabletDefectClassifier(unittest.TestCase):

    def setUp(self):
        self.config = PackConfig(expected_rows=2, expected_cols=5)
        self.classifier = TabletDefectClassifier(self.config)

    def _build_test_pack(self, defect_map=None):
        defect_map = defect_map or {}
        img = create_blister_background(width=700, height=340)
        pad = 20
        card_w = 700 - (2 * pad)
        card_h = 340 - (2 * pad)
        margin_x = int(card_w * 0.05)
        margin_y = int(card_h * 0.05)
        active_w = card_w - (2 * margin_x)
        active_h = card_h - (2 * margin_y)

        cell_w = active_w / 5
        cell_h = active_h / 2

        idx = 1
        for r in range(2):
            for c in range(5):
                cx = int(pad + margin_x + (c + 0.5) * cell_w)
                cy = int(pad + margin_y + (r + 0.5) * cell_h)
                draw_pocket_cavity(img, cx, cy)
                defect = defect_map.get(idx, "NORMAL")
                draw_tablet(img, cx, cy, radius=32, defect_type=defect)
                idx += 1
        return img

    def test_perfect_pack_inspection_passes(self):
        img = self._build_test_pack()
        result = self.classifier.inspect_pack(img, image_name="unit_test_perfect")
        self.assertTrue(result.is_passed)
        self.assertEqual(result.tablets_present, 10)
        self.assertEqual(result.total_defects, 0)

    def test_missing_tablet_triggers_rejection(self):
        img = self._build_test_pack(defect_map={1: "MISSING"})
        result = self.classifier.inspect_pack(img, image_name="unit_test_missing")
        self.assertFalse(result.is_passed)
        self.assertGreater(result.missing_count, 0)

    def test_chipped_tablet_triggers_rejection(self):
        img = self._build_test_pack(defect_map={3: "CHIPPED"})
        result = self.classifier.inspect_pack(img, image_name="unit_test_chipped")
        self.assertFalse(result.is_passed)
        self.assertGreater(result.chipped_count, 0)

    def test_discolored_tablet_triggers_rejection(self):
        img = self._build_test_pack(defect_map={5: "DISCOLORED"})
        result = self.classifier.inspect_pack(img, image_name="unit_test_discolored")
        self.assertFalse(result.is_passed)
        self.assertGreater(result.discolored_count, 0)


if __name__ == "__main__":
    unittest.main()
