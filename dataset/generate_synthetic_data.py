"""
Synthetic Blister Pack Dataset Generator.
Generates realistic 2x5 blister pack images simulating industrial defects:
- Missing tablets
- Chipped / cracked tablets
- Foreign color contamination
- Specular foil gradients and noise
Also outputs a ground_truth.json for automated benchmarking.
"""

import os
import math
import json
from typing import List, Dict, Any, Tuple
import cv2
import numpy as np


def create_blister_background(width: int = 700, height: int = 340) -> np.ndarray:
    """
    Creates a realistic metallic blister pack background with subtle gradient
    and fine foil texture.
    """
    img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Outer conveyor belt (dark charcoal)
    img[:] = (30, 30, 32)

    # Blister card dimensions
    pad = 20
    card_x1, card_y1 = pad, pad
    card_x2, card_y2 = width - pad, height - pad

    # Metallic silver foil gradient across the card (aluminum tones: 110 - 135)
    for y in range(card_y1, card_y2):
        progress = (y - card_y1) / float(card_y2 - card_y1)
        base_val = int(115 + 18 * math.sin(progress * math.pi))
        img[y, card_x1:card_x2] = (base_val - 4, base_val, base_val + 6)

    # Rounded rectangle border for card
    cv2.rectangle(img, (card_x1, card_y1), (card_x2, card_y2), (95, 95, 100), 2)

    # Subtle brushed metal noise
    noise = np.random.normal(0, 3, img.shape).astype(np.int16)
    blended = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    # Restore outer conveyor belt color
    blended[:card_y1, :] = img[:card_y1, :]
    blended[card_y2:, :] = img[card_y2:, :]
    blended[:, :card_x1] = img[:, :card_x1]
    blended[:, card_x2:] = img[:, card_x2:]

    return blended


def draw_pocket_cavity(img: np.ndarray, cx: int, cy: int, radius: int = 42) -> None:
    """Draws an embossed blister pocket cavity (depression in foil)."""
    # Outer cavity rim shadow
    cv2.circle(img, (cx + 1, cy + 2), radius + 4, (75, 75, 80), 2)
    # Inner pocket depression fill (darker metallic recess)
    cv2.circle(img, (cx, cy), radius + 2, (95, 96, 100), -1)


def draw_tablet(
    img: np.ndarray,
    cx: int,
    cy: int,
    radius: int = 32,
    defect_type: str = "NORMAL",
    tablet_color: Tuple[int, int, int] = (240, 240, 242)
) -> None:
    """
    Renders an individual tablet with optional defect geometry.
    """
    if defect_type == "MISSING":
        # Draw empty pocket foil reflection only (no tablet)
        cv2.circle(img, (cx, cy), radius - 10, (85, 86, 90), 1)
        return

    if defect_type == "DISCOLORED":
        # Foreign or contaminated tablet (bright vivid blue/cyan pill)
        tablet_color = (210, 130, 25)  # BGR: blue tablet

    if defect_type == "CHIPPED":
        # Chipped tablet: draw base circle, then subtract a jagged chunk
        canvas = np.zeros(img.shape[:2], dtype=np.uint8)
        cv2.circle(canvas, (cx, cy), radius, 255, -1)
        
        # Cut out upper-right wedge
        pts = np.array([
            [cx, cy],
            [cx + radius + 15, cy - radius - 10],
            [cx + int(radius * 0.2), cy - radius - 10]
        ], dtype=np.int32)
        cv2.fillPoly(canvas, [pts], 0)

        # Draw tablet onto image where canvas is 255
        indices = np.where(canvas > 0)
        for y, x in zip(indices[0], indices[1]):
            dist = math.hypot(x - cx, y - cy)
            shade = 1.0 - (dist / (radius * 4.0))
            color = [min(255, max(0, int(c * shade))) for c in tablet_color]
            img[y, x] = color

        # Tablet rim
        contours, _ = cv2.findContours(canvas, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(img, contours, -1, (170, 170, 175), 1)
        return

    # Normal intact tablet: smooth round tablet with subtle 3D shading
    # Pill drop shadow inside cavity
    cv2.circle(img, (cx + 1, cy + 2), radius, (70, 70, 75), -1)
    
    # Pill body with 3D spherical bevel
    for r in range(radius, 0, -2):
        factor = 0.88 + 0.12 * (1.0 - (r / radius))
        c = tuple(min(255, int(val * factor)) for val in tablet_color)
        cv2.circle(img, (cx, cy), r, c, -1)

    # Embossed bisect score line (common on pharmaceutical tablets)
    cv2.line(img, (cx - radius + 8, cy), (cx + radius - 8, cy), (210, 210, 215), 2)
    # Crisp outer rim
    cv2.circle(img, (cx, cy), radius, (185, 185, 190), 1)


def generate_sample_dataset(output_dir: str) -> Dict[str, Any]:
    """
    Generates all sample blister packs and corresponding ground truth JSON.
    
    Returns:
        Dict representing ground truth annotations.
    """
    os.makedirs(output_dir, exist_ok=True)

    rows, cols = 2, 5
    width, height = 700, 340
    
    # Calculate cell coordinates aligned with grid detector layout
    pad = 20
    card_w = width - (2 * pad)
    card_h = height - (2 * pad)
    margin_x = int(card_w * 0.05)
    margin_y = int(card_h * 0.05)
    active_w = card_w - (2 * margin_x)
    active_h = card_h - (2 * margin_y)

    cell_w = active_w / cols
    cell_h = active_h / rows

    pocket_coords = []
    for r in range(rows):
        for c in range(cols):
            cx = int(pad + margin_x + (c + 0.5) * cell_w)
            cy = int(pad + margin_y + (r + 0.5) * cell_h)
            pocket_coords.append((cx, cy))

    # Scenario definitions
    scenarios = [
        {
            "filename": "sample_01_perfect_pack.png",
            "name": "Perfect Blister Pack",
            "expected_status": "PASS",
            "defects": {}
        },
        {
            "filename": "sample_02_missing_tablet.png",
            "name": "Missing Tablets Scenario",
            "expected_status": "REJECT",
            "defects": {4: "MISSING", 8: "MISSING"}  # 1-indexed pocket indices
        },
        {
            "filename": "sample_03_chipped_tablet.png",
            "name": "Chipped Tablet Scenario",
            "expected_status": "REJECT",
            "defects": {3: "CHIPPED"}
        },
        {
            "filename": "sample_04_discolored_tablet.png",
            "name": "Discolored Tablet Scenario",
            "expected_status": "REJECT",
            "defects": {7: "DISCOLORED"}
        },
        {
            "filename": "sample_05_multi_defect.png",
            "name": "Multi-Defect Compound Scenario",
            "expected_status": "REJECT",
            "defects": {2: "MISSING", 6: "CHIPPED", 9: "DISCOLORED"}
        }
    ]

    ground_truth: Dict[str, Any] = {}

    for sc in scenarios:
        img = create_blister_background(width, height)
        pack_gt = {
            "name": sc["name"],
            "expected_status": sc["expected_status"],
            "pockets": {}
        }

        for idx, (cx, cy) in enumerate(pocket_coords, start=1):
            draw_pocket_cavity(img, cx, cy)
            defect = sc["defects"].get(idx, "NORMAL")
            draw_tablet(img, cx, cy, radius=32, defect_type=defect)
            pack_gt["pockets"][str(idx)] = defect

        save_path = os.path.join(output_dir, sc["filename"])
        cv2.imwrite(save_path, img)
        ground_truth[sc["filename"]] = pack_gt

    gt_path = os.path.join(output_dir, "ground_truth.json")
    with open(gt_path, "w", encoding="utf-8") as f:
        json.dump(ground_truth, f, indent=2)

    return ground_truth


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "samples")
    print(f"Generating synthetic blister pack dataset in: {out_dir}")
    gt = generate_sample_dataset(out_dir)
    print(f"Generated {len(gt)} blister pack test scenarios and ground_truth.json.")
