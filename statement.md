# Project Statement: PharmaCount-CV

## 1. Problem Statement
In high-speed pharmaceutical packaging lines, blister cards are filled and sealed at rates exceeding 200–500 packs per minute. During this packaging process, mechanical feeder failures, tablet breakage, tool wear, and cross-batch contamination can lead to:
- Empty blister pockets (missing tablets),
- Chipped, broken, or fragmented tablets,
- Foreign tablets or chemical discoloration.

Manual visual inspection by human operators is error-prone due to visual fatigue, subjective judgement, and the inability to keep pace with modern packaging lines. A single defective blister pack reaching the consumer can lead to inaccurate dosage, product recalls, regulatory penalties from agencies like the FDA/CDSCO, and severe patient health risks. 

PharmaCount-CV provides a vision-based automated inspection system capable of checking tablet presence, shape integrity, and color consistency in blister packs from digital imagery without human intervention.

## 2. Scope of the Project
The scope of this project includes:
- Automated localization of blister packs and geometric partitioning of the card into individual pocket cells ($R \times C$ layout).
- Robust image preprocessing to suppress specular reflections and foil glare using bilateral filtering and CLAHE.
- Quantitative geometric contour analysis of each tablet (area, perimeter, circularity/roundness, and convex hull solidity) to detect missing or broken/chipped pills.
- Colorimetric verification in perceptual CIE $L^*a^*b^*$ color space using Euclidean $\Delta E$ to identify discolored or foreign tablets.
- Production-ready output generation: real-time visual HUD overlays with color-coded pocket annotations, machine-readable JSON reports, and CSV production audit logs.
- Fully automated command-line execution (CLI) supporting single-image inspection, batch folder processing, and a built-in benchmark evaluation suite.

*Out of Scope:* Physical hardware conveyor control (PLC integration) and blister pocket de-blistering mechanical arms, which are hardware integrations beyond image processing.

## 3. Target Users
- **Pharmaceutical Packaging Engineers & QA Inspectors:** To automate quality control checks at the sealing and cartoning stage.
- **Regulatory Compliance & Audit Officers:** To maintain automated, timestamped digital logs of batch defect rates and fill percentages.
- **Contract Packaging Organizations (CPOs):** Who require flexible, configurable inspection software that can quickly adapt to different blister grid layouts (e.g., $2 \times 5$, $2 \times 7$, $1 \times 10$) without expensive proprietary vision sensor lock-in.

## 4. High-Level Features
- **Deterministic Tablet Verification:** High-precision counting and missing-tablet detection with near 100% recall.
- **Sub-Pixel Shape Integrity Analysis:** Identifies chips, cracks, and structural deformities using circularity and convex hull solidity metrics.
- **Perceptual Color Consistency:** Detects subtle batch discoloration and cross-product contamination using CIE $L^*a^*b^*$ $\Delta E$ comparison against reference tablets.
- **Configurable Grid Profiles:** Supports arbitrary row and column configurations via CLI flags or a structured `config.json` profile.
- **100% Headless CLI Operation:** Runs in any terminal or headless container environment without requiring a GUI display.
- **Automated Synthetic Dataset & Benchmark Suite:** Generates realistic packaging scenarios with ground truth annotations to validate precision, recall, and detection accuracy.
