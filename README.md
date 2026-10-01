# PharmaCount-CV: Vision-Based Blister Pack & Tablet Integrity Inspector

An automated computer vision quality control system designed for high-speed pharmaceutical packaging lines. PharmaCount-CV verifies tablet presence, checks geometric shape integrity (identifying chipped or fractured pills), and validates color uniformity (detecting foreign or chemically degraded tablets) from digital blister pack imagery.

---

## Key Features

- **Automated Pocket Localization:** Segments blister cards into discrete $R \times C$ pocket cavities using adaptive contour bounding and geometric grid projection.
- **Specularity & Glare Suppression:** Utilizes edge-preserving bilateral filtering and CLAHE (Contrast-Limited Adaptive Histogram Equalization) to mitigate reflective silver foil highlights.
- **Quantitative Morphological Inspection:** Computes mathematical shape descriptors (contour area, isoperimetric circularity quotient, and convex hull solidity) to reliably detect broken or chipped tablets.
- **CIE $L^*a^*b^*$ Perceptual Color Grading:** Evaluates color difference using Euclidean $\Delta E$ relative to reference tablets, catching cross-batch contamination and degradation.
- **Headless & CLI-First Design:** Fully executable from terminal environments with zero GUI display dependencies, returning industry-standard exit codes (0 for PASS, 1 for REJECT, 2 for error).
- **Comprehensive Audit Logging:** Automatically exports annotated inspection images with HUD overlays, machine-readable JSON logs, and append-ready CSV production records.
- **Built-in Benchmark Suite:** Includes a synthetic blister pack generator with ground truth annotations to test and verify precision, recall, and detection accuracy.

---

## Technologies & Libraries

- **Language:** Python 3.8+ (tested on Python 3.11)
- **Computer Vision:** OpenCV (`opencv-python` >= 4.8.0)
- **Scientific Computing:** NumPy (>= 1.24.0)
- **Visualization:** Matplotlib (>= 3.7.0)
- **Testing:** Python `unittest` framework

---

## Directory Structure

```
PharmaCount-CV/
├── config.json                     # Default inspection thresholds & grid dimensions
├── main.py                         # Unified CLI entrypoint
├── requirements.txt                # Python package dependencies
├── statement.md                    # Problem statement and project scope document
├── README.md                       # Documentation & execution guide
├── pharmacount/                    # Core library package
│   ├── __init__.py                 # Package exports
│   ├── config.py                   # Dataclasses & configuration parser
│   ├── preprocessor.py             # Bilateral filter, CLAHE & color space conversion
│   ├── grid_detector.py            # Blister card localization & pocket slicing
│   ├── contour_analyzer.py         # Tablet segmentation, circularity & solidity
│   ├── color_inspector.py          # CIE Lab Delta-E color distance inspection
│   ├── defect_classifier.py        # Multi-criteria decision engine (PASS/REJECT)
│   ├── visualizer.py               # HUD overlay, status badges & annotated output
│   └── report_engine.py            # JSON/CSV exporters & terminal ASCII tables
├── dataset/
│   ├── generate_synthetic_data.py  # Realistic blister pack generator with noise
│   └── samples/                    # Test images and ground_truth.json
├── tests/                          # Automated unit and integration test suite
│   ├── test_preprocessor.py        # Preprocessing filters & transformations
│   ├── test_grid_detector.py       # Pocket geometry and bounding tests
│   ├── test_contour_analyzer.py    # Circularity and solidity mathematical tests
│   ├── test_defect_classifier.py   # Decision logic and classification tests
│   └── test_cli_pipeline.py        # End-to-end CLI integration test
└── docs/
    ├── diagrams.md                 # System architecture and UML diagrams (Mermaid)
    └── project_report.md           # 15-section comprehensive project report
```

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/{your-username}/PharmaCount-CV.git
   cd PharmaCount-CV
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## How to Run

### 1. Generate Sample Dataset
To create realistic blister pack scenarios (perfect packs, missing pills, chipped pills, discolored pills) and `ground_truth.json`:
```bash
python main.py --generate-samples
```

### 2. Inspect a Single Blister Pack Image
```bash
python main.py --input dataset/samples/sample_01_perfect_pack.png --output-dir results/
```

### 3. Inspect an Entire Directory of Blister Packs (Batch Mode)
```bash
python main.py --input dataset/samples/ --output-dir results/
```

### 4. Run Benchmark Evaluation Suite
Evaluates all test images against ground truth and outputs precision, recall, and accuracy metrics:
```bash
python main.py --benchmark --output-dir results/
```

### 5. Custom Grid Layout Configuration
Inspect a blister pack with a 2x7 layout:
```bash
python main.py --input path/to/pack.jpg --expected-rows 2 --expected-cols 7
```

---

## Running Unit Tests

Run the full automated test suite using Python's built-in `unittest` runner:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

All 5 test suites will execute, covering edge cases, math calculations, and CLI arguments.

---

## Sample Output

When running an inspection on a blister pack with a missing pill:

```
=================================================================
  PHARMACOUNT-CV INSPECTION AUDIT: sample_02_missing_tablet.png
  STATUS: ✘ REJECT   |   LATENCY: 22.4 ms
=================================================================
  Pocket  Status        Circularity   Solidity    Delta-E   
-----------------------------------------------------------------
  #1      NORMAL        0.884         0.985       4.2       
  #2      NORMAL        0.891         0.991       3.8       
  #3      NORMAL        0.879         0.982       5.1       
  #4      MISSING       N/A           N/A         N/A       
  #5      NORMAL        0.888         0.987       4.0       
  #6      NORMAL        0.892         0.989       3.6       
  #7      NORMAL        0.880         0.981       4.9       
  #8      MISSING       N/A           N/A         N/A       
  #9      NORMAL        0.885         0.986       4.1       
  #10     NORMAL        0.889         0.988       3.9       
-----------------------------------------------------------------
  Summary: Pockets: 10 | Present: 8 | Defects: 2
  Breakdown: Missing: 2 | Chipped: 0 | Discolored: 0
=================================================================
```

Annotated visual files (`annotated_*.png`), structured JSON logs (`report_*.json`), and production audit CSV records (`batch_inspection_log.csv`) are written directly to the specified `--output-dir`.

---

## License

This project is submitted for the Computer Vision course evaluation. All algorithms and implementations are original student work.
