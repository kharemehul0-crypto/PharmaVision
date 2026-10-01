# PharmaCount-CV

Automated blister pack and tablet inspection system built with OpenCV and Python for my Computer Vision flipped course project.

PharmaCount-CV inspects images of pharmaceutical blister packs on packaging lines. It verifies that all pockets are filled, checks that tablets are intact (not chipped or cracked), and checks that tablet colors match the expected batch without discoloration or foreign pills.

---

## What It Does

When an image of a blister pack is passed to the script, it:
1. Locates the blister pack card and divides it into individual pocket cells based on the expected grid layout (e.g. 2 rows by 5 columns).
2. Cleans up lighting reflections from the metallic blister foil using bilateral filtering and CLAHE.
3. Segments each tablet and measures its shape parameters:
   - Area and perimeter
   - Circularity quotient ($4\pi \cdot \text{Area} / \text{Perimeter}^2$)
   - Convex hull solidity ($\text{Area} / \text{Hull Area}$)
4. Samples the color inside the tablet contour and measures the perceptual color distance ($\Delta E$) in CIE $L^*a^*b^*$ space against a reference tablet.
5. Flags any defects:
   - Empty pockets are marked `MISSING` (red crossed box).
   - Broken or chipped pills are marked `CHIPPED` (orange box).
   - Off-color or contaminated pills are marked `DISCOLORED` (purple box).
   - Good tablets are marked `NORMAL` (green box).
6. Outputs an annotated image with a summary status header, an ASCII summary table in the terminal, a JSON report, and a CSV row in the batch audit log.

---

## Tech Stack & Dependencies

- Python 3.8+ (tested on Python 3.11)
- OpenCV (`opencv-python`)
- NumPy
- Matplotlib

Install all requirements with:
```bash
pip install -r requirements.txt
```

---

## Project Structure

```
PharmaCount-CV/
├── config.json                     # Default parameters (grid size, thresholds)
├── main.py                         # CLI script to run inspections
├── requirements.txt                # Dependencies
├── statement.md                    # Project problem statement and scope
├── README.md                       # Setup and usage guide
├── pharmacount/                    # Core inspection library
│   ├── __init__.py
│   ├── config.py                   # Data classes and configuration loader
│   ├── preprocessor.py             # Bilateral filter, CLAHE, and color spaces
│   ├── grid_detector.py            # Card boundary detection and pocket slicing
│   ├── contour_analyzer.py         # Tablet segmentation, circularity, and solidity
│   ├── color_inspector.py          # Color sampling and CIE Lab Delta-E checks
│   ├── defect_classifier.py        # Decision logic for pocket and pack status
│   ├── visualizer.py               # HUD overlay, status banners, and boxes
│   └── report_engine.py            # JSON/CSV file exporters and terminal tables
├── dataset/
│   ├── generate_synthetic_data.py  # Script that creates realistic blister packs
│   └── samples/                    # 5 test scenarios and ground_truth.json
├── tests/                          # Automated unit test suite
│   ├── test_preprocessor.py
│   ├── test_grid_detector.py
│   ├── test_contour_analyzer.py
│   ├── test_defect_classifier.py
│   └── test_cli_pipeline.py
├── docs/
│   ├── project_report.md           # 15-section project report
│   ├── project_report.html         # Formatted HTML report (for PDF printing)
│   ├── diagrams.md                 # System architecture and UML diagrams
│   ├── system_architecture.png     # Pipeline architecture diagram
│   └── terminal_execution_screenshot.png # Terminal execution screenshot
└── results/                        # Output folder for annotated images and logs
```

---

## How to Run

All features are accessible via `main.py` using standard terminal flags.

### 1. Run the benchmark evaluation
Tests the pipeline against 5 test packs in `dataset/samples/` and checks predictions against `ground_truth.json`:
```bash
python main.py --benchmark
```

### 2. Inspect a single image
```bash
python main.py --input dataset/samples/sample_03_chipped_tablet.png
```

### 3. Batch inspect a folder of images
```bash
python main.py --input dataset/samples/ --output-dir results/
```

### 4. Custom grid configuration
If inspecting a blister pack with a different layout (for example, 2 rows of 7 tablets):
```bash
python main.py --input path/to/image.png --expected-rows 2 --expected-cols 7
```

### 5. Generate sample dataset
Recreates the synthetic test images with realistic metallic foil noise:
```bash
python main.py --generate-samples
```

---

## Running the Unit Tests

Run the test suite using Python's built-in `unittest`:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

This runs 13 unit tests covering bilateral filtering, color space conversions, grid pocket indexing, circularity calculations, and CLI execution.

---

## Sample Terminal Output

Inspecting a pack with a chipped tablet (`sample_03_chipped_tablet.png`):

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

The script exits with code `0` if all tablets pass, and `1` if any defect is detected, making it easy to use in automated scripts.
