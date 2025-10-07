
# quadtree_core.py
from __future__ import annotations
from typing import List, Tuple, Dict, Any
from PIL import Image
import json

from a2tree import QuadTree  # OK: core depends on tree. Do NOT import a2main here.


# ---------- Color helpers ----------
def rgb2grayscale(red: int, green: int, blue: int) -> int:
    # same formula you used in a2main.Compressor.rgb2grayscale
    return round(0.2126 * red + 0.7152 * green + 0.0722 * blue)


# ---------- Conversions (PIL <-> matrices) ----------
def pil_to_rgb_matrix(img: Image.Image) -> List[List[Tuple[int,int,int]]]:
    img = img.convert("RGB")
    w, h = img.size
    px = list(img.getdata())
    return [px[i*w:(i+1)*w] for i in range(h)]

def rgb_to_gray_matrix(rgb: List[List[Tuple[int,int,int]]]) -> List[List[int]]:
    return [[rgb2grayscale(r,g,b) for (r,g,b) in row] for row in rgb]

def gray_matrix_to_pil(gray: List[List[int]]) -> Image.Image:
    h = len(gray)
    w = len(gray[0]) if h else 0
    img = Image.new("L", (w, h))
    img.putdata([v for row in gray for v in row])
    return img


# ---------- Core API ----------
def compress_gray(gray: List[List[int]], loss: int, mirror: bool=False) -> tuple[Image.Image, QuadTree]:
    qt = QuadTree(loss)
    qt.build_quad_tree(gray, mirror=mirror)
    recon = qt.convert_to_pixels()
    out_img = gray_matrix_to_pil(recon)  # 'L'
    return out_img, qt

def compress_pil(img: Image.Image, loss: int, mirror: bool=False) -> tuple[Image.Image, QuadTree]:
    rgb = pil_to_rgb_matrix(img)
    gray = rgb_to_gray_matrix(rgb)
    return compress_gray(gray, loss, mirror)

def decompress_from_preorder(preorder_list: List[str], width: int, height: int) -> Image.Image:
    qt = QuadTree.restore_from_preorder(preorder_list, width, height)
    gray = qt.convert_to_pixels()
    return gray_matrix_to_pil(gray)

def serialize_qdt_json(qt: QuadTree) -> Dict[str, Any]:
    return {"width": qt.width, "height": qt.height, "preorder": qt.preorder()}

def deserialize_qdt_json(obj: Dict[str, Any]) -> Image.Image:
    return decompress_from_preorder(obj["preorder"].split(","), int(obj["width"]), int(obj["height"]))


# ---------- Assignment .qdt (binary: BMP-like header + preorder body) ----------
def parse_qdt_binary(data: bytes) -> tuple[QuadTree, int, int]:
    if len(data) < 26:
        raise ValueError("QDT file too small or invalid header.")
    offset = int.from_bytes(data[10:14], "little")
    width  = int.from_bytes(data[18:22], "little")
    height = int.from_bytes(data[22:26], "little")
    if offset < 26 or offset > len(data):
        raise ValueError("Invalid QDT offset.")
    body = data[offset:]
    preorder_list = body.decode("utf-8").split(",")
    qt = QuadTree.restore_from_preorder(preorder_list, width, height)
    return qt, width, height

def to_qdt_json_bytes(qt: QuadTree) -> bytes:
    return json.dumps(serialize_qdt_json(qt), separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def image_to_png_bytes(img: Image.Image) -> bytes:
    import io
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    return buf.getvalue()
