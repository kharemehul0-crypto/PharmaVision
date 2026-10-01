"""
Report Generation and Audit Logging Module.
Exports inspection logs in JSON and CSV formats and formats clean CLI tables.
"""

import os
import csv
import json
from typing import List, Dict, Any
from .config import InspectionResult


class ReportEngine:
    """
    Handles report generation, metrics serialization, and terminal logging.
    """

    @staticmethod
    def save_json(result: InspectionResult, output_path: str) -> None:
        """Saves inspection result as formatted JSON."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, indent=2)

    @staticmethod
    def append_to_csv(result: InspectionResult, csv_path: str) -> None:
        """Appends inspection summary row to a CSV audit file."""
        os.makedirs(os.path.dirname(os.path.abspath(csv_path)), exist_ok=True)
        file_exists = os.path.isfile(csv_path)

        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow([
                    "Image Name",
                    "Overall Status",
                    "Total Pockets",
                    "Tablets Present",
                    "Fill Rate (%)",
                    "Total Defects",
                    "Missing Count",
                    "Chipped Count",
                    "Discolored Count",
                    "Processing Time (ms)"
                ])

            writer.writerow([
                result.image_name,
                "PASS" if result.is_passed else "REJECT",
                result.total_pockets,
                result.tablets_present,
                f"{result.fill_rate_percent:.1f}",
                result.total_defects,
                result.missing_count,
                result.chipped_count,
                result.discolored_count,
                f"{result.processing_time_ms:.2f}"
            ])

    @staticmethod
    def print_terminal_summary(result: InspectionResult) -> None:
        """Prints a clean ASCII summary table to the terminal."""
        status_symbol = "[PASS]" if result.is_passed else "[REJECT]"
        separator = "=" * 65

        print(f"\n{separator}")
        print(f"  PHARMACOUNT-CV INSPECTION AUDIT: {result.image_name}")
        print(f"  STATUS: {status_symbol}   |   LATENCY: {result.processing_time_ms:.1f} ms")
        print(separator)
        print(f"  {'Pocket':<8}{'Status':<14}{'Circularity':<14}{'Solidity':<12}{'Delta-E':<10}")
        print("-" * 65)

        for p in result.pocket_metrics:
            circ_str = f"{p.circularity:.3f}" if p.circularity > 0 else "N/A"
            solid_str = f"{p.solidity:.3f}" if p.solidity > 0 else "N/A"
            delta_str = f"{p.delta_e:.1f}" if p.delta_e < 900 else "N/A"
            
            print(f"  #{p.index:<7}{p.status.value:<14}{circ_str:<14}{solid_str:<12}{delta_str:<10}")

        print("-" * 65)
        print(f"  Summary: Pockets: {result.total_pockets} | Present: {result.tablets_present} | Defects: {result.total_defects}")
        print(f"  Breakdown: Missing: {result.missing_count} | Chipped: {result.chipped_count} | Discolored: {result.discolored_count}")
        print(f"{separator}\n")
