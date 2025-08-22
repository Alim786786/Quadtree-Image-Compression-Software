# Quadtree Image Compression

Lossy grayscale image compression using a **quadtree**. Input: 24-bit **BMP** → Output: `.bmp.qdt`; decompress to `.bmp.qdt.bmp`. Optional **mirror** (bottom half reflected onto top half).

## Quick Start
- Python 3.9+ (`pip install pytest` for tests)
- Input must be **BMP** (24-bit). Convert PNG/JPG first if needed.

```bash
python a2main.py
# Compress
# Command: c
# Loss [0-255]: 25
# Mirror image? [y/N]: n
# File Name: dog.bmp
# -> writes dog.bmp.qdt

# Decompress
# Command: d
# File Name: dog.bmp.qdt
# -> writes dog.bmp.qdt.bmp (grayscale)
