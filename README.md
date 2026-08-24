# 👻 Ghost Invisibility — Computer Vision Project

A real-time computer vision project that creates a **ghost / invisibility effect** using a webcam.

The project captures the background, detects the person using **MediaPipe Selfie Segmentation**, and replaces the detected person with the previously captured background. A **MediaPipe Hands** gesture lets the user toggle invisibility using a thumb + middle-finger pinch.


### Features

- Real-time webcam processing
- Background capture using multiple frames
- Background averaging for a cleaner reference frame
- MediaPipe Selfie Segmentation
- Person-mask post-processing
- Hand landmark detection
- Thumb + middle-finger pinch gesture
- Ghost ON/OFF toggle
- Smooth ghost transition using alpha blending
- Background exposure matching
- Real-time FPS display
- On-screen HUD
- Background-capture progress indicator
- Ghost percentage indicator
- Single-window output

## 🧠 How It Works


Webcam
  │
  ├──► Hand Detection ──► Pinch Distance ──► Ghost Toggle
  │
  ▼
Frame
  │
  ▼
MediaPipe Selfie Segmentation
  │
  ▼
Person Mask
  │
  ├──► Threshold
  ├──► Morphological Closing
  ├──► Dilation
  ├──► Gaussian Blur
  └──► Hand Mask
          │
          ▼
      Final Mask
          │
          ▼
Background Exposure Matching
          │
          ▼
Alpha Compositing
          │
          ▼
      Ghost Frame
          │
          ▼
         HUD
          │
          ▼
       Display
```

## ✨ Ghost Effect

The core compositing operation is conceptually:


Output =
    Live Frame × (1 - Alpha)
    +
    Background × Alpha


When the person mask is strong and Ghost Mode reaches full alpha, the person's pixels are replaced by the captured background.

## ✋ Gesture Control

The current gesture uses:


Thumb tip       → MediaPipe landmark 4
Middle tip      → MediaPipe landmark 12


Their normalized distance is calculated.


Distance < PINCH_THRESHOLD
        ↓
      Pinch
        ↓
   Toggle Ghost


The current pinch threshold is:


PINCH_THRESHOLD = 0.06


The gesture uses a state latch so holding the fingers together does not repeatedly toggle Ghost Mode.

## 🖼️ Background Capture

Press **Space** to start background capture.

The project currently captures:


90 frames


and averages them to create the reference background.

During capture, the HUD displays the progress.

Ghost Mode is disabled until a valid background has been created.

## ⚙️ Current Processing Parameters

Important segmentation parameters in `src/engine.py`:

| Parameter | Current value | Purpose |
|---|---:|---|
| Segmentation threshold | `0.25` | Converts soft person confidence into a binary mask |
| Morphology kernel | `9 × 9` | Closes small gaps in the mask |
| Dilation | `1` iteration | Expands the person mask |
| Gaussian blur | `3 × 3` | Softens mask edges |
| Mask multiplier | `0.9` | Controls mask strength |
| Hand kernel | `15 × 15` | Expands hand mask |
| Hand dilation | `2` | Ensures detected hand is included |
| Background threshold | `0.05` | Selects pixels considered definite background |
| Alpha speed | `0.10` | Controls Ghost ON/OFF transition |
| Pinch threshold | `0.06` | Controls pinch sensitivity |

These values are intentionally exposed in the source so they can be tuned for different cameras and lighting conditions.

## 🛠️ Requirements

- Python 3.9+
- OpenCV
- MediaPipe
- NumPy
- A working webcam

Install dependencies:

```bash
pip install -r requirements.txt
```

## ▶️ Run

From the repository root:

```bash
python src/main.py
```

### Controls

| Control | Action |
|---|---|
| `Space` | Capture background |
| Thumb + middle finger pinch | Toggle Ghost Mode |
| `Esc` | Exit |

## 📁 Project Structure

```text
Ghost_Invisibility/
│
├── src/
│   ├── main.py
│   └── engine.py
│
├── assets/
│   └── demo-placeholder.txt
│
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## 🎯 Project Status

### Completed

- [x] Webcam capture
- [x] Background capture
- [x] Background averaging
- [x] Person segmentation
- [x] Mask processing
- [x] Hand detection
- [x] Pinch gesture
- [x] Ghost ON/OFF
- [x] Smooth alpha transition
- [x] Exposure matching
- [x] HUD
- [x] Background progress display

### Future Improvements

- [ ] Two-hand gesture: spread → pinch → vanish
- [ ] Better edge refinement
- [ ] Improved FPS optimization
- [ ] More robust lighting compensation
- [ ] Configurable camera index and resolution
- [ ] Optional recording/export mode

## ⚠️ Notes

Performance depends on the camera resolution, CPU, MediaPipe processing speed, and lighting conditions.

For the best invisibility effect:

1. Keep the camera fixed.
2. Keep the scene/background relatively static.
3. Capture the background before entering Ghost Mode.
4. Avoid large lighting changes after background capture.
5. Keep the person reasonably separated from the background.

## 📜 License

This project is released under the MIT License. See `LICENSE`.
