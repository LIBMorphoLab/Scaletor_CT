# Scaletor

Batch downscaling tool for grayscale image datasets (TIFF, PNG, BMP). Resizes images using LANCZOS resampling while preserving data integrity.

## Requirements

- Python 3.x
- `Pillow`
- `numpy`

```bash
pip install Pillow numpy
```

## Usage

1. Open `scaletor.py` and set the **User Settings** block:

```python
path = "D:/example/"   # Input directory (use forward slashes, trailing slash required)
new_x = 500            # Target width in pixels (height is auto-calculated to maintain aspect ratio)
workflow = 2           # 1 or 2 (see below)
```

2. Run:

```bash
python scaletor.py
```

## Workflows

| Value | Behavior |
|-------|----------|
| `1`   | Resizes with LANCZOS, outputs in the **original file type and bit depth**. |
| `2`   | Resizes with LANCZOS, applies 1–99 percentile normalization, outputs as **8-bit BMP**. |

## Expected Folder Structure

```
D:/example/
├── Dataset_1/
│   ├── image001.tif
│   ├── image002.tif
│   └── ...
├── Dataset_2/
│   ├── image001.tif
│   └── ...
```

> Each subfolder should contain **only** the image files belonging to that dataset.

## Output

```
D:/example/
├── Dataset_1/
│   ├── image001.tif
│   ├── ...
│   └── scaled/
│       ├── scaled_000.bmp
│       ├── scaled_001.bmp
│       └── _Scaletor_log.txt
├── Dataset_2/
│   └── scaled/
│       └── ...
```

A `_Scaletor_log.txt` file is written into each `scaled/` folder recording the original dimensions, output dimensions, image count, and workflow used.

## Notes

- Only **grayscale** (2-D) images are processed; color images are skipped with a warning.
- Images are converted to signed 32-bit internally before resizing to prevent clipping artifacts from LANCZOS overshoot.
- Processing time ranges from a few seconds to several minutes depending on dataset size.
