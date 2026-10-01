# Project Statement: PharmaCount-CV

## 1. Problem Statement
In pharmaceutical manufacturing, blister cards are filled with tablets and sealed at very high speeds, often several hundred packs every minute. Because the machinery runs so fast, a few common defects happen regularly:
- Pockets get skipped, leaving empty cavities with missing pills.
- Tablets get cracked or chipped by feed chutes or mechanical vibrations before sealing.
- Foreign tablets or discolored pills from previous batches get mixed into the packaging line.

Human operators inspecting these conveyor lines get tired quickly and cannot catch micro-defects at production speed. If a blister pack with missing or broken medication reaches a patient, it can cause incorrect dosages or serious health complications, along with costly recalls for the pharmaceutical company.

I built PharmaCount-CV to automate this inspection process using computer vision. The system analyzes photos of blister cards, counts the tablets, checks their physical shape for cracks or chips, and flags any discolored or foreign pills before the pack leaves the packaging area.

## 2. Scope of the Project
This project covers the image processing and defect detection pipeline for blister pack quality control:
- Automatically finding the blister card in an image and slicing it into an R x C grid of pocket regions.
- Filtering out reflections and glare caused by the shiny aluminum foil using bilateral filtering and CLAHE.
- Calculating geometric metrics (area, circularity, and convex hull solidity) to spot missing or broken tablets.
- Checking tablet colors in CIE L*a*b* color space to detect discoloration or foreign pills.
- Exporting inspection results as visual annotated images (with color-coded boxes and HUD banners), machine-readable JSON logs, and CSV audit files.
- Running entirely through the command line (CLI) so it can run headlessly on any machine or server without needing a desktop GUI.

What is out of scope: Direct hardware control for physical reject kickers (PLCs) and mechanical sorters. This project focuses entirely on the vision and software classification system.

## 3. Target Users
- Quality assurance inspectors and line operators who need an automated check at the packaging stage.
- Compliance teams who need automated, timestamped digital logs of batch defect counts.
- Small or contract packaging facilities looking for a simple, configurable inspection tool that works on standard webcams or industrial camera feeds without expensive proprietary sensor hardware.

## 4. Key Features
- Accurate tablet counting and missing pill detection.
- Broken and chipped tablet identification based on contour shape metrics (circularity and solidity).
- Color deviation checks using Delta-E in CIE L*a*b* space against reference tablet samples.
- Configurable grid layouts (like 2x5, 2x7, or custom layouts) through CLI flags or a simple config.json file.
- Works 100% headlessly in terminals with standard exit codes (0 for pass, 1 for reject).
- Built-in sample generator and automated benchmark suite to test precision, recall, and accuracy across realistic defect scenarios.
