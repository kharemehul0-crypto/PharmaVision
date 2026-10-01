"""
PharmaCount-CV: Vision-Based Pharmaceutical Blister Pack & Tablet Integrity Inspector
Main Command-Line Interface (CLI).
"""

import os
import sys
import argparse
import glob
import json
from typing import List, Dict, Any
import cv2

from pharmacount.config import PackConfig, TabletStatus
from pharmacount.preprocessor import ImagePreprocessor
from pharmacount.defect_classifier import TabletDefectClassifier
from pharmacount.visualizer import InspectionVisualizer
from pharmacount.report_engine import ReportEngine
from dataset.generate_synthetic_data import generate_sample_dataset


def run_benchmark(output_dir: str, config: PackConfig) -> None:
    """
    Evaluates PharmaCount-CV against the ground truth dataset and computes
    precision, recall, accuracy, and F1-score.
    """
    samples_dir = os.path.join(os.path.dirname(__file__), "dataset", "samples")
    gt_path = os.path.join(samples_dir, "ground_truth.json")

    if not os.path.exists(gt_path):
        print("[*] Sample dataset not found. Generating now...")
        generate_sample_dataset(samples_dir)

    with open(gt_path, "r", encoding="utf-8") as f:
        ground_truth: Dict[str, Any] = json.load(f)

    classifier = TabletDefectClassifier(config)
    visualizer = InspectionVisualizer()

    total_tablets = 0
    correct_predictions = 0
    true_defects = 0
    predicted_defects = 0
    true_positive_defects = 0  # correctly identified defect

    print("\n" + "=" * 70)
    print("  PHARMACOUNT-CV BENCHMARK EVALUATION ACROSS TEST SCENARIOS")
    print("=" * 70)
    print(f"  {'Filename':<32}{'Expected':<12}{'Predicted':<12}{'Match?'}")
    print("-" * 70)

    for filename, meta in ground_truth.items():
        img_path = os.path.join(samples_dir, filename)
        img = cv2.imread(img_path)
        if img is None:
            continue

        result = classifier.inspect_pack(img, image_name=filename)
        expected_status = meta["expected_status"]
        pred_status = "PASS" if result.is_passed else "REJECT"
        match_str = "[YES]" if expected_status == pred_status else "[NO]"

        print(f"  {filename:<32}{expected_status:<12}{pred_status:<12}{match_str}")

        # Save annotated result
        annotated = visualizer.render_overlay(img, result)
        out_path = os.path.join(output_dir, f"annotated_{filename}")
        cv2.imwrite(out_path, annotated)

        # Pocket-level evaluation
        pockets_gt = meta["pockets"]
        for p in result.pocket_metrics:
            gt_status = pockets_gt.get(str(p.index), "NORMAL")
            pred_pocket_status = p.status.value

            total_tablets += 1
            if gt_status == pred_pocket_status:
                correct_predictions += 1

            is_gt_defect = (gt_status != "NORMAL")
            is_pred_defect = (pred_pocket_status != "NORMAL")

            if is_gt_defect:
                true_defects += 1
            if is_pred_defect:
                predicted_defects += 1
            if is_gt_defect and is_pred_defect:
                true_positive_defects += 1

    accuracy = (correct_predictions / total_tablets) * 100.0 if total_tablets > 0 else 0.0
    precision = (true_positive_defects / predicted_defects) * 100.0 if predicted_defects > 0 else 100.0
    recall = (true_positive_defects / true_defects) * 100.0 if true_defects > 0 else 100.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    print("-" * 70)
    print(f"  Total Pockets Evaluated:    {total_tablets}")
    print(f"  Pocket Classification Acc:  {accuracy:.2f}%")
    print(f"  Defect Detection Precision: {precision:.2f}%")
    print(f"  Defect Detection Recall:    {recall:.2f}%")
    print(f"  F1-Score:                   {f1:.2f}%")
    print("=" * 70)
    print(f"  Annotated visual outputs saved to: {output_dir}\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="PharmaCount-CV: Vision-Based Blister Pack & Tablet Integrity Inspector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python main.py --generate-samples
  python main.py --benchmark
  python main.py --input dataset/samples/sample_01_perfect_pack.png
  python main.py --input dataset/samples/ --output-dir results/
"""
    )
    parser.add_argument("--input", "-i", type=str, help="Path to single image or directory of images")
    parser.add_argument("--output-dir", "-o", type=str, default="results", help="Directory for output images and logs")
    parser.add_argument("--config", "-c", type=str, help="Path to custom configuration JSON file")
    parser.add_argument("--expected-rows", type=int, help="Override expected blister pack rows")
    parser.add_argument("--expected-cols", type=int, help="Override expected blister pack columns")
    parser.add_argument("--save-json", action="store_true", default=True, help="Save machine-readable JSON reports")
    parser.add_argument("--save-csv", action="store_true", default=True, help="Append inspection results to CSV log")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress terminal ASCII summary")
    parser.add_argument("--generate-samples", action="store_true", help="Generate synthetic sample blister pack dataset")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark against ground truth test suite")

    args = parser.parse_args()

    # Load configuration
    if args.config and os.path.exists(args.config):
        config = PackConfig.from_file(args.config)
    elif os.path.exists("config.json"):
        config = PackConfig.from_file("config.json")
    else:
        config = PackConfig()

    if args.expected_rows:
        config.expected_rows = args.expected_rows
    if args.expected_cols:
        config.expected_cols = args.expected_cols

    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    # Action 1: Generate synthetic dataset
    if args.generate_samples:
        samples_dir = os.path.join(os.path.dirname(__file__), "dataset", "samples")
        print(f"[*] Generating synthetic blister pack dataset in {samples_dir}...")
        generate_sample_dataset(samples_dir)
        print("[OK] Dataset generation completed successfully.")
        if not args.input and not args.benchmark:
            return 0

    # Action 2: Run benchmark
    if args.benchmark:
        run_benchmark(args.output_dir, config)
        return 0

    # Action 3: Inspect image or folder
    if not args.input:
        print("[!] No input provided. Running benchmark by default (use -h for options).")
        run_benchmark(args.output_dir, config)
        return 0

    # Gather images
    target_files: List[str] = []
    if os.path.isdir(args.input):
        for ext in ("*.png", "*.jpg", "*.jpeg", "*.bmp"):
            target_files.extend(glob.glob(os.path.join(args.input, ext)))
    elif os.path.isfile(args.input):
        target_files.append(args.input)
    else:
        print(f"[ERR] Error: Input path does not exist: {args.input}")
        return 2

    if not target_files:
        print(f"[ERR] Error: No images found matching: {args.input}")
        return 2

    classifier = TabletDefectClassifier(config)
    visualizer = InspectionVisualizer()
    preprocessor = ImagePreprocessor(config)

    overall_failures = 0

    for img_path in target_files:
        filename = os.path.basename(img_path)
        try:
            bgr = preprocessor.load_image(img_path)
        except Exception as e:
            print(f"[ERR] Error loading {img_path}: {e}")
            overall_failures += 1
            continue

        result = classifier.inspect_pack(bgr, image_name=filename)
        if not result.is_passed:
            overall_failures += 1

        # Save annotated image
        annotated = visualizer.render_overlay(bgr, result)
        out_img_path = os.path.join(args.output_dir, f"annotated_{filename}")
        cv2.imwrite(out_img_path, annotated)

        # Save JSON report
        if args.save_json:
            base_name, _ = os.path.splitext(filename)
            json_path = os.path.join(args.output_dir, f"report_{base_name}.json")
            ReportEngine.save_json(result, json_path)

        # Save CSV audit
        if args.save_csv:
            csv_path = os.path.join(args.output_dir, "batch_inspection_log.csv")
            ReportEngine.append_to_csv(result, csv_path)

        # Terminal output
        if not args.quiet:
            ReportEngine.print_terminal_summary(result)
            print(f"  [+] Saved annotated overlay: {out_img_path}")

    # Exit code: 0 if all packs passed, 1 if any pack had defects (industry standard exit code)
    return 1 if overall_failures > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
