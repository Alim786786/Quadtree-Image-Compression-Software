"""
Assignment 2: Quadtree Compression

=== CSC148 Summer 2025 ===
Department of Mathematical and Computational Sciences,
University of Toronto Mississauga

=== Module Description ===
This module contains the compressor and decompressor classes.
"""

from typing import List, Tuple

from a2files import QuadTreeFile, BMPFile, BMP_EXTENSION, QDT_EXTENSION
from a2tree import QuadTree

MIRROR_IMG = False

class Compressor:
    """
    The class used to perform the compression operation
    """
    bmp_filename: str   # the name of the BMP file to compress
    loss_level: int     # this loss_level provided by the user

    def __init__(self, bmp_filename: str, loss_level: int) -> None:

        if not bmp_filename.endswith(BMP_EXTENSION):
            raise RuntimeError(
                'bmp_filename must end with {}'.format(BMP_EXTENSION))
        if not 0 <= loss_level <= 255:
            raise RuntimeError(
                'loss_rate must be between 0 and 255, inclusive')
        self.bmp_filename = bmp_filename
        self.loss_level = loss_level
        return

    def run(self) -> None:
        """
        Run the compressor
        """

        bmp_file = BMPFile(self.bmp_filename)
        bmp_file.load()

        # The body of the bmp file has each pixels as a triple, we will convert
        # to triple to a single value that will be used as r, b and g. This
        # means the colour is converted into greyscale.
        pixels_single = self.convert_grayscale_single(bmp_file.body)
        qd_tree = self.compress(pixels_single, self.loss_level)
        qdt_file = QuadTreeFile('{}{}'.format(self.bmp_filename, QDT_EXTENSION))
        qdt_file.set_data(
            offset=bmp_file.offset,
            width=bmp_file.width,
            height=bmp_file.height,
            header=bmp_file.header,
            body=qd_tree
        )
        qdt_file.save()
        return

    @staticmethod
    def compress(pixels: List[List[int]], loss_level: int) -> QuadTree:
        """
        Compress by building the quad tree
        """
        tree = QuadTree(loss_level)
        print("mirror =", MIRROR_IMG)
        tree.build_quad_tree(pixels, MIRROR_IMG)
        return tree

    @staticmethod
    def convert_grayscale_single(
            pixels: List[List[Tuple[int, int, int]]]) -> List[List[int]]:
        """
        Converting triples to singles.
        """
        res = list()
        for row in pixels:
            res_row = list()
            for (r, g, b) in row:
                gray = Compressor.rgb2grayscale(r, g, b)
                res_row.append(gray)
            res.append(res_row)
        return res

    @staticmethod
    def rgb2grayscale(red: int, green: int, blue: int):
        """
        Convert a RGB colour triple to a single grayscale value
        Why this particular formula? Read the following link for more info.
        https://en.wikipedia.org/wiki/Grayscale
        """
        return round(0.2126 * red + 0.7152 * green + 0.0722 * blue)


class Decompressor:
    """
    The class used to perform the decompression operation
    """
    qdt_filename: str   # the name of the QDT file to decompress

    def __init__(self, qdt_filename: str) -> None:

        if not qdt_filename.endswith(QDT_EXTENSION):
            raise RuntimeError(
                'Decompressor.__init__: qdt_filename must end with {}'.format(
                    QDT_EXTENSION))
        self.qdt_filename = qdt_filename
        return

    def run(self) -> None:
        """
        Run the decompressor
        """

        qdt_file = QuadTreeFile(self.qdt_filename)
        qdt_file.load()
        pixels_single = self.decompress(qdt_file.body)
        pixels_triple = self.greyscale_single_to_triple(pixels_single)
        bmp_file = BMPFile('{}{}'.format(self.qdt_filename, BMP_EXTENSION))
        bmp_file.set_data(
            offset=qdt_file.offset,
            width=qdt_file.width,
            height=qdt_file.height,
            header=qdt_file.header,
            body=pixels_triple)
        bmp_file.save()

    @staticmethod
    def decompress(qd_tree: QuadTree) -> List[List[int]]:
        """
        Decompress by converting the tree into pixels
        """
        return qd_tree.convert_to_pixels()

    @staticmethod
    def greyscale_single_to_triple(pixels_single: List[List[int]]) \
            -> List[List[Tuple[int, int, int]]]:
        """
        Convert singles to triples
        """
        res = list()
        for row in pixels_single:
            res_row = list()
            for gray in row:
                res_row.append((gray, gray, gray))
            res.append(res_row)
        return res


if __name__ == '__main__':

    # TODO: Write your user-interface code here
    import os
    import sys

    def ask(prompt: str, allow_blank: bool = False) -> str:
        while True:
            s = input(prompt).strip()
            if s.lower() == 'q':
                print('Bye!')
                sys.exit(0)
            if s or allow_blank:
                return s
            print('Please enter a value (or q to quit).')

    print("\nQuad Tree Image Compression")
    print("============================")
    print("Input 'q' at any point to terminate the app\n")

    while True:
        cmd = ask("Command [c -> Compress | d -> Decompress] : ").lower()
        if cmd not in ('c', 'd'):
            print("Please type 'c' or 'd' (or q to quit).\n")
            continue

        try:
            if cmd == 'c':
                # --- Compress ---
                loss_raw = ask("Loss [between 0-255] : ")
                if not loss_raw.isdigit():
                    raise RuntimeError("Loss must be an integer in 0–255.")
                loss = int(loss_raw)
                if not (0 <= loss <= 255):
                    raise RuntimeError("Loss must be in 0–255.")

                mirror_ans = ask("Mirror image? [y/N] : ", allow_blank=True).lower()
                MIRROR_IMG = (mirror_ans == 'y')

                bmp_name = ask("File Name: ").strip()
                if not bmp_name.endswith(BMP_EXTENSION):
                    raise RuntimeError(f"Filename must end with {BMP_EXTENSION}")
                if not os.path.exists(bmp_name):
                    raise RuntimeError(f"File not found: {bmp_name}")

                print(f"Compressing {bmp_name}")
                comp = Compressor(bmp_name, loss)
                comp.run()  # prints 'mirror = ...' internally

                out_name = f"{bmp_name}{QDT_EXTENSION}"
                if os.path.exists(out_name):
                    in_size = os.path.getsize(bmp_name)
                    out_size = os.path.getsize(out_name)
                    ratio = (out_size / in_size) if in_size else float('inf')
                    print(f"Input size: {in_size:,} bytes")
                    print(f"Output size: {out_size:,} bytes")
                    print(f"Compression ratio: {ratio:.3f} (smaller is better)")

                print("Compression done.\n")

            else:
                # --- Decompress ---
                qdt_name = ask("File Name: ").strip()
                if not qdt_name.endswith(QDT_EXTENSION):
                    raise RuntimeError(f"Filename must end with {QDT_EXTENSION}")
                if not os.path.exists(qdt_name):
                    raise RuntimeError(f"File not found: {qdt_name}")

                print(f"Decompressing {qdt_name}")
                decomp = Decompressor(qdt_name)
                decomp.run()

                out_name = f"{qdt_name}{BMP_EXTENSION}"
                if os.path.exists(out_name):
                    in_size = os.path.getsize(qdt_name)
                    out_size = os.path.getsize(out_name)
                    print(f"Input size: {in_size:,} bytes")
                    print(f"Output size: {out_size:,} bytes")
                print("Decompression done.\n")

        except Exception as e:
            print(f"Error: {e}\n")
