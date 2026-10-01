"""
Generates a clean, publication-grade System Architecture diagram for PharmaCount-CV
and saves it to docs/system_architecture.png.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def create_architecture_diagram(output_path: str):
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.5)
    ax.axis("off")

    # Colors
    c_blue = "#2980b9"
    c_teal = "#16a085"
    c_purple = "#8e44ad"
    c_orange = "#d35400"
    c_green = "#27ae60"
    c_gray_bg = "#f8f9fa"
    c_card_border = "#bdc3c7"

    # Title
    ax.text(6.0, 7.15, "PHARMACOUNT-CV: SYSTEM ARCHITECTURE", 
            ha="center", va="center", fontsize=15, fontweight="bold", color="#2c3e50")
    ax.text(6.0, 6.85, "Modular Sequential Pipeline for Blister Pack Automated Optical Inspection (AOI)", 
            ha="center", va="center", fontsize=10, style="italic", color="#7f8c8d")

    # Pipeline Stages Boxes (Containers)
    stages = [
        ("STAGE 1: Ingestion & Preprocessing", 0.5, 4.3, 3.2, 2.1, c_blue),
        ("STAGE 2: Spatial Lattice Slicing", 4.4, 4.3, 3.2, 2.1, c_teal),
        ("STAGE 3: Feature Extraction", 8.3, 4.3, 3.2, 2.1, c_purple),
        ("STAGE 4: Multi-Criteria Defect Decision", 2.2, 1.2, 3.6, 2.2, c_orange),
        ("STAGE 5: Presentation & Audit Logs", 6.8, 1.2, 4.2, 2.2, c_green),
    ]

    for title, x, y, w, h, col in stages:
        # Container background
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.15",
                                     facecolor=c_gray_bg, edgecolor=col, linewidth=2.0)
        ax.add_patch(box)
        # Header banner
        header = patches.FancyBboxPatch((x, y + h - 0.42), w, 0.42, 
                                        boxstyle="round,pad=0.04,rounding_size=0.1",
                                        facecolor=col, edgecolor="none")
        ax.add_patch(header)
        ax.text(x + w / 2.0, y + h - 0.21, title, ha="center", va="center", 
                fontsize=8.5, fontweight="bold", color="white")

    # Stage 1 Sub-items
    s1_text = [
        "Image Ingestion (CLI / Batch)",
        "Bilateral Denoising (d=9, s=75)",
        "CLAHE Adaptive Equalization",
        "BGR -> HSV & CIE L*a*b* Transforms"
    ]
    for i, t in enumerate(s1_text):
        ax.text(0.7, 5.8 - i * 0.38, f"• {t}", fontsize=7.8, color="#34495e")

    # Stage 2 Sub-items
    s2_text = [
        "Card Outer Boundary Localization",
        "Packaging Margin Trimming",
        "R x C Grid Geometric Projection",
        "Individual Pocket ROI Slicing"
    ]
    for i, t in enumerate(s2_text):
        ax.text(4.6, 5.8 - i * 0.38, f"• {t}", fontsize=7.8, color="#34495e")

    # Stage 3 Sub-items
    s3_text = [
        "Contour Segmentation (Otsu)",
        "Circularity (4*pi*A / P^2)",
        "Solidity (A / Convex_Hull)",
        "CIE Delta-E Color Distance"
    ]
    for i, t in enumerate(s3_text):
        ax.text(8.5, 5.8 - i * 0.38, f"• {t}", fontsize=7.8, color="#34495e")

    # Stage 4 Sub-items
    s4_text = [
        "Occupancy < 20%  -->  MISSING",
        "Circ < 0.76 or Solid < 0.90  -->  CHIPPED",
        "Delta-E > 28.0  -->  DISCOLORED",
        "All Checks Compliant  -->  NORMAL",
        "Overall Pack Aggregation: PASS / REJECT"
    ]
    for i, t in enumerate(s4_text):
        ax.text(2.4, 2.85 - i * 0.35, f"• {t}", fontsize=7.5, color="#2c3e50", fontweight="bold" if i==4 else "normal")

    # Stage 5 Sub-items
    s5_text = [
        "Visual HUD Overlays (Green/Red/Orange/Purple)",
        "Diagnostic Summary ASCII Table in Terminal",
        "Structured Machine-Readable JSON Export",
        "Relational CSV Production Audit Trail Log",
        "Standard CLI Exit Codes (0: PASS, 1: REJECT)"
    ]
    for i, t in enumerate(s5_text):
        ax.text(7.0, 2.85 - i * 0.35, f"• {t}", fontsize=7.5, color="#34495e")

    # Connector Arrows
    arrow_props = dict(facecolor="#7f8c8d", edgecolor="#34495e", width=1.8, headwidth=6, headlength=7)
    
    # 1 -> 2
    ax.annotate("", xy=(4.4, 5.35), xytext=(3.7, 5.35), arrowprops=arrow_props)
    # 2 -> 3
    ax.annotate("", xy=(8.3, 5.35), xytext=(7.6, 5.35), arrowprops=arrow_props)
    # 3 -> 4 (down and left)
    ax.annotate("", xy=(5.8, 3.4), xytext=(9.5, 4.3),
                arrowprops=dict(facecolor="#7f8c8d", edgecolor="#34495e", width=1.8, headwidth=6, headlength=7,
                                connectionstyle="arc3,rad=-0.15"))
    # 4 -> 5
    ax.annotate("", xy=(6.8, 2.3), xytext=(5.8, 2.3), arrowprops=arrow_props)

    plt.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] System architecture diagram generated at: {output_path}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(base_dir, "docs", "system_architecture.png")
    create_architecture_diagram(out)
