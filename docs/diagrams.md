# PharmaCount-CV: System Architecture & UML Design Diagrams

This document contains formal software architecture and design diagrams for the **PharmaCount-CV** inspection system.

---

## 1. System Architecture Diagram

```mermaid
flowchart TD
    subgraph Ingestion["1. Image Ingestion"]
        A["Blister Pack Image (Disk / Stream)"] --> B["ImagePreprocessor"]
    end

    subgraph Preprocessing["2. Preprocessing & Conditioning"]
        B --> B1["Bilateral Denoising (Grain Suppression)"]
        B1 --> B2["CLAHE (Adaptive Contrast Equalization)"]
        B2 --> B3["Color Space Decomposition (BGR / HSV / Lab)"]
    end

    subgraph Localization["3. Spatial Segmentation"]
        B3 --> C["BlisterGridDetector"]
        C --> C1["Card Perimeter Localization"]
        C1 --> C2["Lattice Grid Partitioning (R x C)"]
        C2 --> C3["Pocket ROI Extraction"]
    end

    subgraph Analysis["4. Feature Extraction & Inspection"]
        C3 --> D1["TabletContourAnalyzer"]
        C3 --> D2["TabletColorInspector"]
        D1 --> D1a["Contour Segmentation & Morphological Opening"]
        D1a --> D1b["Geometric Descriptors (Area, Circularity, Solidity)"]
        D2 --> D2a["Contour Masked Sampling"]
        D2a --> D2b["CIE Lab Euclidean Delta-E Calculation"]
    end

    subgraph Decision["5. Defect Classification & Decision Engine"]
        D1b --> E["TabletDefectClassifier"]
        D2b --> E
        E --> E1{"Defect Evaluation"}
        E1 -->|Occupancy < 20%| E2["MISSING"]
        E1 -->|Area/Circ/Solid Deficit| E3["CHIPPED"]
        E1 -->|Delta-E > Threshold| E4["DISCOLORED"]
        E1 -->|All Metrics Compliant| E5["NORMAL"]
    end

    subgraph Presentation["6. Presentation & Audit Logging"]
        E2 & E3 & E4 & E5 --> F["InspectionVisualizer"]
        E2 & E3 & E4 & E5 --> G["ReportEngine"]
        F --> H["Annotated Inspection Image (HUD Overlay)"]
        G --> I["JSON Machine-Readable Audit Log"]
        G --> J["CSV Production Database Append"]
        G --> K["Terminal ASCII Summary Table"]
    end
```

---

## 2. Process Flow / Workflow Diagram

```mermaid
flowchart TD
    Start(["Start Inspection Job"]) --> LoadImg["Load Image from CLI --input"]
    LoadImg --> CheckValid{"Image Valid?"}
    CheckValid -->|No| LogErr["Log Error & Return Exit Code 2"] --> EndFail(["Halt"])
    CheckValid -->|Yes| ApplyBilateral["Apply Bilateral Filter to Suppress Foil Noise"]
    ApplyBilateral --> FindCard["Detect Blister Card Outer Boundary"]
    FindCard --> SubdivideGrid["Subdivide Active Area into R x C Pocket Cells"]
    
    SubdivideGrid --> LoopPockets["For Each Pocket Cell (1 to N)"]
    LoopPockets --> SegmentTablet["Segment Tablet Contour via Otsu + Elliptical Opening"]
    SegmentTablet --> CheckContour{"Contour Found?"}
    
    CheckContour -->|No / Area < 20%| MarkMissing["Assign Status: MISSING"]
    CheckContour -->|Yes| CalcGeometry["Calculate Area, Perimeter, Circularity, Solidity"]
    
    CalcGeometry --> CheckShape{"Circularity & Solidity >= Tolerance?"}
    CheckShape -->|No| MarkChipped["Assign Status: CHIPPED / BROKEN"]
    CheckShape -->|Yes| CalcColor["Extract Mean CIE Lab & Calculate Delta-E"]
    
    CalcColor --> CheckColor{"Delta-E <= Max Allowed?"}
    CheckColor -->|No| MarkDiscolored["Assign Status: DISCOLORED"]
    CheckColor -->|Yes| MarkNormal["Assign Status: NORMAL"]
    
    MarkMissing & MarkChipped & MarkDiscolored & MarkNormal --> MorePockets{"More Pockets?"}
    MorePockets -->|Yes| LoopPockets
    MorePockets -->|No| AggregateStatus["Aggregate Pack Status (PASS if 0 Defects else REJECT)"]
    
    AggregateStatus --> RenderHUD["Render Visual HUD Overlays & Pocket Bounding Boxes"]
    RenderHUD --> SaveOutputs["Save Annotated Image, JSON Audit, CSV Record"]
    SaveOutputs --> PrintSummary["Print Terminal ASCII Summary Table"]
    PrintSummary --> EndSuccess(["Return Exit Code (0: PASS, 1: REJECT)"])
```

---

## 3. UML Use Case Diagram

```mermaid
flowchart LR
    QA_Inspector["QA Inspector / Line Operator"]
    Auto_Pipeline["CI / Automated Packaging Pipeline"]
    Audit_Officer["Regulatory Audit Officer"]

    subgraph PharmaCount_CV["PharmaCount-CV System"]
        UC1(["Inspect Blister Pack Image"])
        UC2(["Batch Inspect Image Directory"])
        UC3(["Configure Inspection Tolerances (config.json)"])
        UC4(["Run Benchmark Validation Suite"])
        UC5(["Export Production Audit Logs (CSV / JSON)"])
        UC6(["Generate Synthetic Test Scenarios"])
    end

    QA_Inspector --> UC1
    QA_Inspector --> UC2
    QA_Inspector --> UC3
    Auto_Pipeline --> UC1
    Auto_Pipeline --> UC2
    Auto_Pipeline --> UC4
    Auto_Pipeline --> UC5
    Audit_Officer --> UC5
    Auto_Pipeline --> UC6
```

---

## 4. UML Class Diagram

```mermaid
classDiagram
    class PackConfig {
        +int expected_rows
        +int expected_cols
        +int bilateral_d
        +float clahe_clip_limit
        +float min_area_ratio
        +float min_circularity
        +float min_solidity
        +tuple reference_color_bgr
        +float max_delta_e
        +to_dict() dict
        +from_file(json_path) PackConfig
    }

    class TabletStatus {
        <<enumeration>>
        NORMAL
        MISSING
        CHIPPED
        DISCOLORED
    }

    class PocketMetric {
        +int index
        +int row
        +int col
        +tuple bbox
        +TabletStatus status
        +float area
        +float perimeter
        +float circularity
        +float solidity
        +float delta_e
        +tuple mean_bgr
        +str defect_reason
        +to_dict() dict
    }

    class InspectionResult {
        +str image_name
        +bool is_passed
        +int total_pockets
        +int tablets_present
        +int missing_count
        +int chipped_count
        +int discolored_count
        +float processing_time_ms
        +List~PocketMetric~ pocket_metrics
        +total_defects() int
        +fill_rate_percent() float
        +to_dict() dict
    }

    class ImagePreprocessor {
        -PackConfig config
        -cv2.CLAHE clahe
        +load_image(path) np.ndarray
        +denoise_bilateral(img) np.ndarray
        +enhance_contrast_clahe(gray) np.ndarray
        +convert_color_spaces(img) tuple
        +segment_pack_mask(img) np.ndarray
    }

    class BlisterGridDetector {
        -PackConfig config
        +find_pack_boundary(img) tuple
        +extract_pockets(img, pack_box) List~PocketMetric~
        +crop_pocket_roi(img, bbox) np.ndarray
    }

    class TabletContourAnalyzer {
        -PackConfig config
        +segment_tablet_contour(pocket_roi) tuple
        +compute_shape_metrics(contour, shape) dict
    }

    class TabletColorInspector {
        -PackConfig config
        -np.ndarray reference_lab
        +extract_tablet_color(pocket_roi, contour) tuple
        +is_color_compliant(delta_e) bool
    }

    class TabletDefectClassifier {
        -PackConfig config
        -BlisterGridDetector grid_detector
        -TabletContourAnalyzer contour_analyzer
        -TabletColorInspector color_inspector
        +inspect_pack(img, name) InspectionResult
    }

    class InspectionVisualizer {
        -dict COLOR_MAP
        +render_overlay(img, result) np.ndarray
        -_draw_pocket(img, pocket)
        -_draw_hud_banner(img, result) np.ndarray
    }

    class ReportEngine {
        +save_json(result, path)
        +append_to_csv(result, path)
        +print_terminal_summary(result)
    }

    TabletDefectClassifier --> PackConfig
    TabletDefectClassifier --> BlisterGridDetector
    TabletDefectClassifier --> TabletContourAnalyzer
    TabletDefectClassifier --> TabletColorInspector
    TabletDefectClassifier ..> InspectionResult : creates
    InspectionResult *-- PocketMetric
    PocketMetric o-- TabletStatus
    InspectionVisualizer ..> InspectionResult : consumes
    ReportEngine ..> InspectionResult : consumes
```

---

## 5. UML Sequence Diagram (Single Inspection Run)

```mermaid
sequenceDiagram
    autonumber
    actor CLI as User / CLI Runner
    participant Main as main.py
    participant Prep as ImagePreprocessor
    participant Clf as TabletDefectClassifier
    participant Grid as BlisterGridDetector
    participant Contour as TabletContourAnalyzer
    participant Color as TabletColorInspector
    participant Vis as InspectionVisualizer
    participant Rep as ReportEngine

    CLI->>Main: python main.py --input pack.png
    Main->>Prep: load_image("pack.png")
    Prep-->>Main: image_bgr
    Main->>Clf: inspect_pack(image_bgr, "pack.png")
    
    Clf->>Grid: find_pack_boundary(image_bgr)
    Grid-->>Clf: pack_box (x, y, w, h)
    Clf->>Grid: extract_pockets(image_bgr, pack_box)
    Grid-->>Clf: List[PocketMetric] (1..N)

    loop For each pocket in grid
        Clf->>Grid: crop_pocket_roi(image_bgr, bbox)
        Grid-->>Clf: pocket_roi
        Clf->>Contour: segment_tablet_contour(pocket_roi)
        Contour-->>Clf: (contour, mask)
        Clf->>Contour: compute_shape_metrics(contour)
        Contour-->>Clf: {area, circularity, solidity}
        
        alt Area < Empty Threshold
            Clf->>Clf: Set Status = MISSING
        else
            Clf->>Color: extract_tablet_color(pocket_roi, contour)
            Color-->>Clf: (mean_bgr, delta_e)
            
            alt Circularity < 0.76 or Solidity < 0.90
                Clf->>Clf: Set Status = CHIPPED
            else if delta_e > 28.0
                Clf->>Clf: Set Status = DISCOLORED
            else
                Clf->>Clf: Set Status = NORMAL
            end
        end
    end

    Clf-->>Main: InspectionResult (pockets, counts, PASS/REJECT)
    Main->>Vis: render_overlay(image_bgr, result)
    Vis-->>Main: annotated_bgr
    Main->>Rep: print_terminal_summary(result)
    Main->>Rep: save_json(result, "results/report_pack.json")
    Main->>Rep: append_to_csv(result, "results/batch_inspection_log.csv")
    Main-->>CLI: Return Exit Code (0 or 1)
```

---

## 6. Storage & Database Schema Design (Production Audit Log)

For regulatory compliance (FDA 21 CFR Part 11 and CDSCO electronic audit standards), all inspection records are persisted across two structures:

### A. Relational Schema / CSV Production Table: `batch_inspection_log`

| Column Name | Data Type | Constraint | Description |
|:---|:---|:---|:---|
| `inspection_id` | `VARCHAR(36)` | PRIMARY KEY / UUID | Unique inspection transaction identifier |
| `timestamp_utc` | `DATETIME` | NOT NULL | ISO 8601 inspection timestamp |
| `image_name` | `VARCHAR(255)` | NOT NULL | Source image filename |
| `overall_status` | `VARCHAR(10)` | CHECK IN ('PASS', 'REJECT') | Batch acceptance decision |
| `total_pockets` | `INT` | NOT NULL, >= 1 | Configured pocket count |
| `tablets_present` | `INT` | NOT NULL, >= 0 | Tablets detected inside pockets |
| `fill_rate_percent`| `DECIMAL(5,2)` | 0.00 to 100.00 | Packaging fill percentage |
| `total_defects` | `INT` | NOT NULL, >= 0 | Total anomalous pockets |
| `missing_count` | `INT` | NOT NULL, >= 0 | Empty pockets count |
| `chipped_count` | `INT` | NOT NULL, >= 0 | Broken/chipped tablets count |
| `discolored_count`| `INT` | NOT NULL, >= 0 | Foreign/degraded tablets count |
| `latency_ms` | `DECIMAL(6,2)`| NOT NULL | Total computer vision processing latency |

### B. Hierarchical Audit Record: `report_{image_name}.json`

```json
{
  "image_name": "sample_03_chipped_tablet.png",
  "overall_status": "REJECT",
  "summary": {
    "total_pockets": 10,
    "tablets_present": 10,
    "fill_rate_percent": 100.0,
    "total_defects": 1,
    "missing_count": 0,
    "chipped_count": 1,
    "discolored_count": 0,
    "processing_time_ms": 23.4
  },
  "pockets": [
    {
      "index": 1,
      "grid_position": { "row": 1, "col": 1 },
      "bounding_box": { "x": 68, "y": 48, "w": 88, "h": 88 },
      "status": "NORMAL",
      "area_px": 3216.5,
      "perimeter_px": 204.2,
      "circularity": 0.884,
      "solidity": 0.985,
      "color_delta_e": 3.8,
      "mean_bgr": [238.1, 238.4, 239.0],
      "defect_reason": "Compliant"
    },
    {
      "index": 3,
      "grid_position": { "row": 1, "col": 3 },
      "bounding_box": { "x": 268, "y": 48, "w": 88, "h": 88 },
      "status": "CHIPPED",
      "area_px": 2410.0,
      "perimeter_px": 218.4,
      "circularity": 0.635,
      "solidity": 0.812,
      "color_delta_e": 4.1,
      "mean_bgr": [237.5, 237.9, 238.2],
      "defect_reason": "Low circularity (0.64); Low solidity (0.81)"
    }
  ]
}
```
