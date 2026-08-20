"""
Polargraph 2D Plotter — Image to Vector Path
---------------------------------------------
Converts an input image into a set of (x_mm, y_mm) waypoints that the
plotter firmware can draw, using edge detection + contour extraction.

Output:
  vectors.txt         -> waypoints, one "x y" per line, blank line
                          between separate strokes/contours
  vector_preview.png  -> visual preview of the extracted path
"""

import cv2
import numpy as np

# ---------- Parameters ----------
INPUT_IMAGE = "hat.jpeg"     # source image
DRAW_W = 50.0                # drawable width in mm
DRAW_H = 50.0                # drawable height in mm
RESIZE_DIM = (500, 500)      # working resolution for edge detection
CANNY_LOW = 80
CANNY_HIGH = 160
SMOOTH_EPS = 2.0              # approxPolyDP tolerance (higher = simpler path)
MIN_CONTOUR_POINTS = 10       # ignore tiny noise contours

OUTPUT_VECTORS = "vectors.txt"
OUTPUT_PREVIEW = "vector_preview.png"


def load_and_preprocess(path):
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Could not load image: {path}")
    img = cv2.resize(img, RESIZE_DIM)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, CANNY_LOW, CANNY_HIGH)
    _, edges = cv2.threshold(edges, 127, 255, cv2.THRESH_BINARY)
    return edges


def extract_contours(edges):
    contours, _ = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )
    smoothed = []
    for c in contours:
        if len(c) > MIN_CONTOUR_POINTS:
            smoothed.append(cv2.approxPolyDP(c, SMOOTH_EPS, True))
    return smoothed


def write_vectors(contours, w, h, out_path):
    with open(out_path, "w") as f:
        for contour in contours:
            for point in contour:
                x_pix, y_pix = point[0]
                x_mm = (x_pix / w) * DRAW_W
                y_mm = DRAW_H - (y_pix / h) * DRAW_H  # flip Y for plotter frame
                f.write(f"{x_mm:.2f} {y_mm:.2f}\n")
            f.write("\n")  # separator between strokes


def save_preview(contours, shape, out_path):
    preview = np.zeros(shape, dtype=np.uint8)
    cv2.drawContours(preview, contours, -1, 255, 1)
    cv2.imwrite(out_path, preview)
    return preview


def main():
    edges = load_and_preprocess(INPUT_IMAGE)
    h, w = edges.shape

    contours = extract_contours(edges)
    write_vectors(contours, w, h, OUTPUT_VECTORS)
    preview = save_preview(contours, (h, w), OUTPUT_PREVIEW)

    cv2.imshow("Vector Path Preview", preview)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
