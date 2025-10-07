
# streamlit_app.py
import json
import time
import streamlit as st
from PIL import Image

from quadtree_core import (
    compress_pil,
    deserialize_qdt_json,
    serialize_qdt_json,
    parse_qdt_binary,
    image_to_png_bytes,
)

st.set_page_config(page_title="Quadtree Image Compressor", layout="wide")

st.title("🧩 Quadtree Image Compressor")
st.caption("Shared core logic powers both this UI and the CLI. Lossy grayscale via recursive quadtrees.")

tab_compress, tab_decompress = st.tabs(["Compress", "Decompress"])

# --------- COMPRESS ----------
with tab_compress:
    with st.sidebar:
        st.header("Compression Settings")
        uploaded = st.file_uploader("Upload an image", type=["png","jpg","jpeg","bmp","tif","tiff"], key="img")
        loss = st.slider("Loss level (0–255)", 0, 255, 25, 1, help="Higher → more compression (more blockiness).")
        mirror = st.toggle("Mirror bottom half onto top", value=False)
        run_btn = st.button("Compress", type="primary")

    col1, col2 = st.columns(2, gap="large")

    if uploaded is not None:
        original_img = Image.open(uploaded)
        col1.subheader("Original")
        col1.image(original_img, use_container_width=True)

        if run_btn:
            t0 = time.time()
            out_img, qt = compress_pil(original_img, loss, mirror)
            elapsed = time.time() - t0

            col2.subheader("Compressed (grayscale)")
            col2.image(out_img.convert("RGB"), use_container_width=True)

            # --- Bytes under images (PNG-normalized for fair comparison) ---
            orig_png_bytes = image_to_png_bytes(original_img)
            comp_png_bytes = image_to_png_bytes(out_img)
            ratio = len(comp_png_bytes) / max(1, len(orig_png_bytes))

            col1.caption(f"Original (PNG bytes): **{len(orig_png_bytes):,}**")
            col2.caption(f"Compressed (PNG bytes): **{len(comp_png_bytes):,}**  •  Ratio: **{ratio:.2f}×**")

            # (Optional) also show raw uploaded file size (uncomment if desired)
            # raw_upload_bytes = len(uploaded.getvalue())
            # st.caption(f"Uploaded file raw bytes: **{raw_upload_bytes:,}** (for reference)")

            st.markdown("---")
            m1, m2 = st.columns(2)
            m1.metric("Runtime", f"{elapsed*1000:.1f} ms")
            m2.metric("Tree nodes", f"{qt.tree_size():,}")

            # Downloads
            st.download_button(
                "⬇️ Download Compressed Image (PNG)",
                data=comp_png_bytes,
                file_name="compressed_quadtree.png",
                mime="image/png",
                use_container_width=True
            )

            st.download_button(
                "⬇️ Download .qdt.json (width/height + preorder)",
                data=json.dumps(serialize_qdt_json(qt), separators=(",", ":"), ensure_ascii=False).encode("utf-8"),
                file_name="compressed_quadtree.qdt.json",
                mime="application/json",
                use_container_width=True
            )
    else:
        st.info("Upload an image to get started.")

# --------- DECOMPRESS ----------
with tab_decompress:
    st.subheader("Decompress from a compressed file")
    st.caption("Upload either **.qdt.json** (portable) or your original **.qdt** binary.")

    qdt_file = st.file_uploader("Upload .qdt.json or .qdt", type=["json","qdt"])
    go = st.button("Decompress", type="primary")

    if qdt_file is not None and go:
        try:
            data = qdt_file.read()
            name = qdt_file.name.lower()
            in_compressed_bytes = len(data)  # raw size of uploaded compressed file

            if name.endswith(".json"):
                img = deserialize_qdt_json(json.loads(data.decode("utf-8")))
                source_fmt = "QDT.JSON"
            else:
                qt, w, h = parse_qdt_binary(data)
                img = Image.new("L", (w, h))
                img.putdata([v for row in qt.convert_to_pixels() for v in row])
                source_fmt = "QDT"

            st.success(f"Decompressed successfully from {source_fmt}.")
            st.image(img.convert("RGB"), caption="Reconstructed (grayscale)", use_container_width=True)

            # --- Bytes under image: compressed file bytes -> reconstructed PNG bytes ---
            recon_png_bytes = image_to_png_bytes(img)
            st.caption(
                f"Compressed file bytes: **{in_compressed_bytes:,}**  →  "
                f"Reconstructed PNG bytes: **{len(recon_png_bytes):,}**"
            )

            # Download reconstructed
            st.download_button(
                "⬇️ Download Reconstructed Image (PNG)",
                data=recon_png_bytes,
                file_name="reconstructed_quadtree.png",
                mime="image/png",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Failed to decompress: {e}")
    elif qdt_file is None:
        st.info("Upload a compressed file, then click Decompress.")
