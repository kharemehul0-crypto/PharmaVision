# PharmaVision

Automated blister pack and tablet inspection system using OpenCV and Python.

- **Author:** Mehul Khare
- **Registration Number:** 24BAI10613
- **Course:** Computer Vision (Flipped Course Project)
- **Repository:** https://github.com/kharemehul0-crypto/PharmaVision

---

## Overview

In pharmaceutical packaging lines, tablets are placed into blister pockets and heat-sealed with aluminum backing foil at rates often exceeding 300 to 500 cards per minute. Because the line moves so rapidly, mechanical chute jams, vibration impacts, or vacuum feeder misfires can lead to:
- Empty pockets (missing pills)
- Cracked, broken, or chipped tablets
- Foreign tablets or chemically discolored pills

Manual inspection by line workers causes eye strain within minutes, and subtle edge chips or faint color variations easily pass through undetected. 

I developed **PharmaVision** to automate this inspection using classical computer vision. Instead of needing high-end GPUs or massive labeled datasets for deep learning, PharmaVision uses geometric contour moments, bilateral filtering, and CIE L*a*b* color distance ($\Delta E$). It runs on a standard laptop CPU in roughly 20 milliseconds per pack (~50 FPS), providing deterministic, real-time quality grading with zero GPU requirements.

---

## How It Works

1. **Card Localization & Pocket Slicing:** Finds the outer contour of the blister card, trims packaging border margins, and projects a uniform $R \times C$ grid to isolate each pocket cavity as an independent region of interest.
2. **Noise & Glare Filtering:** Shiny aluminum foil produces specular glare under overhead lighting. The pipeline uses an edge-preserving bilateral filter ($d=9, \sigma=75$) to smooth foil texture without blurring the crisp outer tablet edge, paired with CLAHE for illumination normalization.
3. **Shape Integrity Analysis:** Segments candidate tablet contours and computes mathematical descriptors:
   - Isoperimetric Circularity Quotient: $C = \frac{4 \pi \cdot \text{Area}}{\text{Perimeter}^2}$ (Normal tablet $\approx 0.88 - 0.95$; chipped tablet $< 0.70$)
   - Convex Hull Solidity: $S = \frac{\text{Area}}{\text{Convex Hull Area}}$ (Normal tablet $\approx 0.98 - 1.00$; chipped tablet $< 0.90$ due to edge fracture indentations)
4. **Perceptual Color Verification:** Erodes the tablet mask by 2 pixels to avoid sampling the metallic pocket rim, converts pixels to CIE L*a*b* space, and computes Euclidean color distance ($\Delta E$) against a reference tablet. If $\Delta E > 28.0$, the pill is flagged as discolored or foreign.
5. **Multi-Criteria Classification:**
   - Empty cavity $\rightarrow$ `MISSING` (Red crossed box)
   - Area, circularity, or solidity deficit $\rightarrow$ `CHIPPED` (Orange box)
   - Delta-E exceeds threshold $\rightarrow$ `DISCOLORED` (Purple box)
   - All tests pass $\rightarrow$ `NORMAL` (Green box)
6. **Reporting:** Attaches a visual HUD banner, outputs a clean ASCII summary table in the terminal, exports a machine-readable JSON log, and appends a row to a batch CSV audit trail.

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kharemehul0-crypto/PharmaVision.git
   cd PharmaVision
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Only `opencv-python`, `numpy`, and `matplotlib` are required)*

---

## Usage Guide

All functions run through `main.py` using standard terminal flags.

### 1. Run the Automated Benchmark Suite
Evaluates all 5 test scenarios in `dataset/samples/` against `ground_truth.json` and reports precision, recall, accuracy, and F1-score:
```bash
python main.py --benchmark
```

### 2. Inspect a Single Blister Pack Image
```bash
python main.py --input dataset/samples/sample_03_chipped_tablet.png
```

### 3. Batch Inspect an Entire Directory
```bash
python main.py --input dataset/samples/ --output-dir results/
```

### 4. Custom Grid Configurations
For blister cards with different row and column layouts (e.g. 2 rows of 7 tablets):
```bash
python main.py --input path/to/pack.jpg --expected-rows 2 --expected-cols 7
```

### 5. Recreate Synthetic Test Dataset
Generates fresh blister pack test images with simulated foil noise and ground truth annotations:
```bash
python main.py --generate-samples
```

---

## Running Unit Tests

Run the full automated test suite using Python's built-in `unittest` runner:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```
All 13 unit tests pass in ~1.5s, covering bilateral filtering, CLAHE, grid pocket indexing, circularity calculations, and CLI subprocess execution.

---

## Sample Diagnostic Terminal Output

Inspecting a blister pack with a fractured tablet (`sample_03_chipped_tablet.png`):

```
=================================================================
  PHARMACOUNT-CV INSPECTION AUDIT: sample_03_chipped_tablet.png
  STATUS: [REJECT]   |   LATENCY: 23.7 ms
=================================================================
  Pocket  Status        Circularity   Solidity    Delta-E   
-----------------------------------------------------------------
  #1      NORMAL        0.903         0.989       13.4      
  #2      NORMAL        0.903         0.989       13.4      
  #3      CHIPPED       0.594         0.889       30.9      
  #4      NORMAL        0.903         0.989       13.4      
  #5      NORMAL        0.903         0.989       13.4      
  #6      NORMAL        0.903         0.989       13.4      
  #7      NORMAL        0.903         0.989       13.4      
  #8      NORMAL        0.903         0.989       13.4      
  #9      NORMAL        0.903         0.989       13.4      
  #10     NORMAL        0.903         0.989       13.4      
-----------------------------------------------------------------
  Summary: Pockets: 10 | Present: 10 | Defects: 1
  Breakdown: Missing: 0 | Chipped: 1 | Discolored: 0
=================================================================
```

### Exit Codes for CI/CD Integration
- `0`: All blister packs passed quality checks (`PASS`).
- `1`: One or more defective blister packs were detected (`REJECT`).
- `2`: Invalid input path or image loading error.
