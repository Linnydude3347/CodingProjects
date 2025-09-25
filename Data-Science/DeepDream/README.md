# Deep Dream (TensorFlow) — Data Analysis Toolkit

A clean, configurable **DeepDream** implementation in **TensorFlow 2** using **InceptionV3** features, with:
- **Tiled gradients** for high‑res images (avoids OOM and seam artifacts)
- **Octaves** (multi‑scale) and **jitter**
- Optional **total variation** smoothing
- Simple **CLI** (`python -m deepdream.cli ...`)

> Tip: Start with a moderate resolution (e.g., 1280px max side) and a `tile-size` ~256–512.

## Quickstart
```bash
cd deep_dream_tf
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
```

### Run DeepDream
```bash
# Minimal
python -m deepdream.cli       --input path/to/input.jpg       --output outputs/dream.jpg

# Customized: stronger effect, more detail
python -m deepdream.cli       --input path/to/input.jpg       --output outputs/dream_strong.jpg       --layers mixed3,mixed5,mixed7       --octaves 4       --octave-scale 1.4       --steps-per-octave 60       --step-size 0.01       --tile-size 512       --tv-weight 0.0005       --jitter 16
```

### Options
- `--layers` — Comma‑separated InceptionV3 layer names (defaults: `mixed3,mixed5`).
- `--octaves` / `--octave-scale` — Number of scales and per‑octave scaling factor.
- `--steps-per-octave` — Gradient ascent iterations per octave.
- `--step-size` — Ascent step (typical 0.005–0.02).
- `--tile-size` — Gradient tiling size (≥ 96 due to Inception min size; try 256–512).
- `--tv-weight` — Total variation smoothing strength (0 to disable).
- `--jitter` — Pixel jitter to reduce tiling seams (e.g., 8–24).
- `--seed` — PRNG seed for reproducibility.

## Notes
- Uses `tf.keras.applications.InceptionV3` (ImageNet weights). Layer picks like `mixed3`, `mixed5`, `mixed7` work well.
- For very large images, raise `--tile-size` and use more octaves to keep each step stable.
- Total variation regularization (`--tv-weight`) can reduce high‑frequency noise.