# Polargraph — Pendulum-Style 2D Plotter

A cord-driven **polargraph** plotter that converts any input image into a hand-drawn line sketch — built for **Build A Bot 3.0**.

Instead of a belt-and-rail Cartesian gantry, this plotter suspends a pen gondola from **two cords, each spooled by its own stepper motor**. By winding and unwinding the two cords in a coordinated sequence, the pen's position is triangulated across the drawing surface — the same principle used by classic pendulum/polargraph drawing machines. A servo lifts and lowers the pen between strokes so travel moves don't leave stray lines. The result is a low-cost, minimal-hardware plotter that can reproduce any image as a continuous set of vector strokes.

---

## How It Works

The project has two halves — **image processing (offline, on a PC)** and **motion control (on the plotter itself)**.

### 1. Image → Vector Path (Python + OpenCV)
- Load and resize the input image
- Convert to grayscale and run **Canny edge detection**
- Extract contours (`cv2.findContours`)
- Simplify each contour with `cv2.approxPolyDP` to remove noisy/redundant points
- Rescale pixel coordinates into real-world millimeters based on the plotter's drawable area
- Export the final path as a list of `(x_mm, y_mm)` points to a `vectors.txt` file, with blank lines separating each stroke/contour
- Generate a preview render (`vector_preview.png`) so you can sanity-check the output before sending it to hardware

### 2. Vector Path → Physical Drawing (Arduino/ESP32 + Steppers + Servo)
- Two **28BYJ-48 stepper motors**, each driven through a **ULN2003 driver board**, wind/unwind the two cords holding the pen gondola
- Motors are stepped through a full-step 4-phase sequence, with each cord's direction and length controlled independently so the gondola traces coordinated curves across the drawing surface
- A **servo motor** lifts the pen off the paper during travel moves and lowers it while drawing, so gaps between strokes don't leave stray lines
- The `vectors.txt` output from the Python stage feeds the motor control loop, converting each `(x_mm, y_mm)` waypoint into the corresponding cord-length change (i.e. step count) for both motors

---

## 🛠️ Hardware Used
| Component | Purpose |
|---|---|
| 2× 28BYJ-48 Stepper Motor | Wind/unwind the two cords driving the pen gondola |
| 2× ULN2003 Driver Board | Power/control the steppers |
| 1× Servo Motor (SG90 or similar) | Pen lift (up/down) mechanism |
| Microcontroller (Arduino / ESP32) | Runs the motion control firmware |
| Pen/marker + gondola + cords + frame | The actual drawing mechanism |

---

## 📁 Repository Structure
```
├── firmware/
│   ├── pen_control.ino        # Servo pen up/down control
│   └── plotter_motion.ino     # Dual-stepper coordinated motion control
├── image_processing/
│   └── image_to_vectors.py    # Image → edge detection → vector path pipeline
├── output/
│   ├── vectors.txt            # Generated (x, y) waypoints in mm
│   └── vector_preview.png     # Visual preview of the traced path
└── README.md
```

---

## 🚀 Usage

**1. Generate the drawing path from an image:**
```bash
python image_to_vectors.py
```
This produces `vectors.txt` (the coordinate path) and a preview image so you can check the line quality before plotting.

**2. Flash the firmware:**
Upload `plotter_motion.ino` (and pen control logic) to your microcontroller, feeding in the generated `vectors.txt` path.

**3. Plot:**
Power up the motors and servo, load paper, and let the arms trace the image — pen down for drawing strokes, pen up for travel moves.

---

## 🎥 Inspiration
Design inspired by polargraph/pendulum-style plotter builds like [this one](https://www.youtube.com/watch?v=T0jwdrgVBBc) — reworked here with a from-scratch image processing pipeline and coordinated dual-cord stepper control.

---

## 🏆 Built For
Built for **Build A Bot 3.0**.

---

## 📌 Notes / Future Improvements
- Tune `stepDelay` for smoother vs. faster drawing
- Add acceleration/deceleration ramping for cleaner curves
- Calibrate cord-length-to-step mapping and motor spacing for more accurate triangulation
- Support SVG input directly instead of raster images
- Add photos/GIFs of the plotter mid-draw and finished output once available
