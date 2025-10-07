# Quadtree Image Compression - Setup Guide

## Quick Start

### Option 1: Web Interface (Recommended)
```bash
pip install streamlit pillow
streamlit run streamlit_app.py
```
Then open your browser to `http://localhost:8501`

### Option 2: Python API
```python
from quadtree_core import compress_pil, decompress_from_preorder
from PIL import Image

# Compress an image
img = Image.open("your_image.jpg")
compressed_img, quadtree = compress_pil(img, loss_level=25)

# Save compressed data
import json
compressed_data = {
    "width": quadtree.width,
    "height": quadtree.height, 
    "preorder": quadtree.preorder()
}
with open("compressed.qdt.json", "w") as f:
    json.dump(compressed_data, f)

# Decompress
with open("compressed.qdt.json", "r") as f:
    data = json.load(f)
reconstructed = decompress_from_preorder(
    data["preorder"].split(","), 
    data["width"], 
    data["height"]
)
```

## Features

- **Lossy compression** using quadtree decomposition
- **Grayscale conversion** with standard RGB weights
- **Configurable loss levels** (0-255, higher = more compression)
- **Optional mirroring** (bottom half reflected onto top)
- **Multiple formats**: PNG, JPG, BMP, TIFF input; PNG output
- **Web interface** with real-time preview
- **Portable format** (.qdt.json) for easy sharing

## Requirements

- Python 3.7+
- Pillow (PIL)
- Streamlit (for web interface)

## File Structure

- `streamlit_app.py` - Web interface
- `quadtree_core.py` - Core compression/decompression logic
- `README.md` - Main documentation
- `.gitignore` - Excludes private implementation files

## How It Works

1. **Input**: Any image format (PNG, JPG, BMP, etc.)
2. **Convert**: RGB → Grayscale using standard weights
3. **Compress**: Recursive quadtree decomposition
   - Calculate standard deviation of each region
   - If std dev ≤ loss_level → create leaf node (average value)
   - If std dev > loss_level → subdivide into 4 quadrants
4. **Output**: Compressed quadtree structure + reconstructed image

## Compression Quality

- **Loss level 0**: Minimal compression, maximum quality
- **Loss level 25**: Balanced compression/quality
- **Loss level 100+**: High compression, blocky results

The algorithm trades image quality for file size reduction - this is expected behavior for lossy compression.
