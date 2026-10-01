# PharmaVision

A command-line tool that checks blister packs for missing, broken and discoloured tablets. It uses OpenCV and plain Python, with no GPU and no trained model.

| | |
|---|---|
| **Author** | Mehul Khare (24BAI10631) |
| **Course** | Computer Vision, flipped course project |
| **Repository** | https://github.com/kharemehul0-crypto/PharmaVision |

---

## Why I built this

On a packaging line, tablets are dropped into blister pockets and sealed under aluminium foil at 300 to 500 cards a minute. At that speed a jammed chute, a vibration knock or a feeder misfire can leave you with:

- empty pockets
- cracked, broken or chipped tablets
- the wrong tablet, or one that has changed colour

A person watching the belt gets tired within minutes, and a small chip or a faint colour shift is easy to miss.

I wanted to see how far classical computer vision could go on this problem. PharmaVision uses contour geometry, a bilateral filter and colour distance in CIE L\*a\*b\* space. It needs no labelled dataset and no GPU. On a normal laptop CPU it handles a pack in about 20 ms, which is roughly 50 packs per second. Because every decision comes from a measurable number, you can always see why a pack was rejected.

---

## How it works

The program goes through each pack in six steps.

**1. Find the card and cut it into pockets.**
It locates the outline of the blister card, trims the packaging border, and lays an R x C grid over the card. Each cell is treated as its own small image.

**2. Clean up the glare.**
Shiny foil reflects overhead light and adds grainy texture. A bilateral filter (d = 9, sigma = 75) smooths that texture but keeps the sharp edge of the tablet. CLAHE then evens out the lighting.

**3. Check the shape.**
The tablet contour in each pocket is measured with two numbers:

- **Circularity** = 4 x pi x Area / Perimeter². A healthy tablet scores about 0.88 to 0.95. A chipped one drops below 0.70.
- **Solidity** = Area / Convex hull area. A healthy tablet scores about 0.98 to 1.00. A fracture leaves dents in the outline and pulls it below 0.90.

**4. Check the colour.**
The tablet mask is eroded by 2 pixels so the metal rim of the pocket is not sampled. The remaining pixels are converted to L\*a\*b\* and compared with a reference tablet. If the distance (delta-E) is above 28.0, the tablet is flagged as discoloured or foreign.

**5. Decide what each pocket is.**

| Finding | Label | Box colour |
|---|---|---|
| Empty cavity | `MISSING` | Red, crossed |
| Area, circularity or solidity too low | `CHIPPED` | Orange |
| Delta-E over the limit | `DISCOLORED` | Purple |
| Everything within limits | `NORMAL` | Green |

If every pocket is `NORMAL`, the pack passes. Otherwise it is rejected.

**6. Write the results.**
You get an annotated image with a summary banner, a table in the terminal, a JSON log for the pack, and a new row in a batch CSV file for auditing.

---

## Getting started

```bash
git clone https://github.com/kharemehul0-crypto/PharmaVision.git
cd PharmaVision
pip install -r requirements.txt
```

Everything runs through `main.py`. No display is needed, so it also works over SSH or in a CI job.

---

## Usage

**Run the built-in benchmark.** This checks the 5 sample scenarios in `dataset/samples/` against `ground_truth.json` and prints accuracy, precision, recall and F1.

```bash
python main.py --benchmark
```

**Inspect one image:**

```bash
python main.py --input dataset/samples/sample_03_chipped_tablet.png
```

**Inspect a whole folder:**

```bash
python main.py --input dataset/samples/ --output-dir results/
```

**Use a different card layout.** For example, 2 rows of 7 tablets:

```bash
python main.py --input path/to/pack.jpg --expected-rows 2 --expected-cols 7
```

**Regenerate the synthetic test images.** These come with simulated foil noise and matching ground-truth labels.

```bash
python main.py --generate-samples
```

---

## Example output

Here is a pack with one fractured tablet (`sample_03_chipped_tablet.png`):

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

Pocket 3 is labelled `CHIPPED` because its circularity (0.594) is under 0.70 and its solidity (0.889) is under 0.90.

---

## Exit codes

These make it easy to use in shell scripts and CI pipelines.

| Code | Meaning |
|---|---|
| `0` | Every pack passed (`PASS`) |
| `1` | At least one pack was rejected (`REJECT`) |
| `2` | Bad input path or the image could not be loaded |

```bash
python main.py --input dataset/samples/ || echo "Something was rejected"
```

---

## Tests

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

All 13 tests pass in about 1.5 seconds. They cover bilateral filtering, CLAHE, pocket indexing in the grid, circularity maths and running the CLI as a subprocess.

---

## Known limits

- The benchmark images are synthetic, so the 100% scores show the logic works but do not predict results on a real line.
- The grid assumes a flat, front-on photo. A tilted card will throw off the pocket positions.
- Thresholds (circularity, solidity, delta-E 28.0) were tuned on the sample set and should be re-tuned for a new tablet type or lighting setup.

## Ideas for later

- Correct tilted cards with a four-point homography.
- Check the foil seal for tiny cracks using texture features.
- Trigger a reject arm through GPIO or Modbus.
