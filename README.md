# 👻 Ghost Invisibility

A real-time **Computer Vision project** that creates a ghost/invisibility effect using a webcam.

The application captures the background, detects the person using **MediaPipe Selfie Segmentation**, and replaces the detected person with the previously captured background. Users can control the effect using a **thumb + middle-finger pinch gesture**.

The project also includes advanced features such as **two-hand gestures, edge refinement, lighting compensation, smooth transitions, FPS monitoring, and video recording**.

---

## ✨ Features

* 🎥 Real-time webcam processing
* 🖼️ Multi-frame background capture
* 📊 Background frame averaging
* 🧍 MediaPipe Selfie Segmentation
* 🎭 Person-mask refinement
* ✋ MediaPipe Hand Landmark Detection
* 🤏 Thumb + middle-finger pinch gesture
* 👐 Optional two-hand gesture mode
* 👻 Ghost ON/OFF toggle
* 🌫️ Smooth ghost transition using alpha blending
* 💡 Background exposure and lighting matching
* ✨ Edge refinement and mask feathering
* 🎬 Optional video recording
* 📈 Real-time FPS display
* 🖥️ On-screen HUD
* 📊 Background-capture progress indicator
* 👻 Ghost percentage indicator
* ⚙️ Centralized configuration
* 🚀 Real-time performance optimization

---

## 🧠 How It Works

The project combines **webcam processing, image segmentation, hand tracking, gesture recognition, image masking, and alpha compositing**.

```text
                         WEBCAM
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
           FRAME                   HAND DETECTION
              │                           │
              │                    LANDMARK EXTRACTION
              │                           │
              │                    PINCH DETECTION
              │                           │
              │                    GESTURE TOGGLE
              │                           │
              ▼                           │
     SELFIE SEGMENTATION                  │
              │                           │
              ▼                           │
        PERSON MASK                       │
              │                           │
       ┌──────┴──────┐                    │
       ▼             ▼                    │
   Threshold     Morphology               │
       │             │                    │
       └──────┬──────┘                    │
              ▼                           │
          Dilation                        │
              │                           │
              ▼                           │
       Gaussian Blur                      │
              │                           │
              ▼                           │
       Edge Refinement                    │
              │                           │
              └──────────┬────────────────┘
                         ▼
                    FINAL MASK
                         │
                         ▼
             LIGHTING / EXPOSURE
                COMPENSATION
                         │
                         ▼
                  ALPHA BLENDING
                         │
                         ▼
                    GHOST FRAME
                         │
                 ┌───────┴───────┐
                 ▼               ▼
                HUD           RECORDER
                 │               │
                 └───────┬───────┘
                         ▼
                      DISPLAY
```

---

## 👻 Ghost Effect

The invisibility effect is created using alpha compositing.

Conceptually:

```text
Output =
    Live Frame × (1 - Alpha)
    +
    Background × Alpha
```

The segmentation mask determines which pixels should be replaced by the captured background.

When Ghost Mode reaches full alpha, the detected person's region is replaced with the background:

```text
Live Person
     ↓
Person Segmentation
     ↓
Refined Mask
     ↓
Captured Background
     ↓
Invisible Person 👻
```

The transition is gradual rather than instantaneous.

```text
Ghost OFF
    ↓
  25%
    ↓
  50%
    ↓
  75%
    ↓
 100%
    ↓
Ghost ON
```

---

## ✋ Gesture Control

The primary gesture uses **MediaPipe Hands**.

The project tracks:

```text
Thumb Tip       → Landmark 4
Middle Finger   → Landmark 12
```

The normalized distance between the two landmarks is calculated.

```text
Distance < PINCH_THRESHOLD
           ↓
         Pinch
           ↓
    Toggle Ghost Mode
```

Default threshold:

```python
PINCH_THRESHOLD = 0.06
```

A gesture latch prevents the application from repeatedly toggling Ghost Mode while the user continues holding the pinch.

### Gesture Flow

```text
READY
  ↓
Pinch detected
  ↓
GHOST ON
  ↓
Fingers remain together
  ↓
No repeated toggle
  ↓
Fingers released
  ↓
READY
```

---

## 👐 Two-Hand Gesture

An optional two-hand interaction is also supported.

The advanced gesture follows:

```text
Two hands detected
        ↓
Hands spread apart
        ↓
Hands move together
        ↓
Pinch
        ↓
Ghost activation
```

Two-hand gesture mode can be enabled or disabled through the configuration.

---

## 🖼️ Background Capture

Press **`Space`** to start background capture.

By default, the application captures:

```text
90 frames
```

The frames are averaged to create a cleaner reference background.

During capture, the HUD displays progress:

```text
CAPTURING BACKGROUND

██████████████░░░░░░

72 / 90
```

Ghost Mode remains disabled until a valid background has been created.

### Best Results

1. Keep the camera stationary.
2. Move completely out of the frame.
3. Press `Space`.
4. Wait until background capture finishes.
5. Enter the scene.
6. Use the pinch gesture to activate Ghost Mode.
7. Avoid major lighting changes.

---

## 🎭 Mask Processing

The MediaPipe segmentation output is a soft confidence mask.

The mask is refined using multiple image-processing operations:

```text
MediaPipe Segmentation
          ↓
Confidence Threshold
          ↓
Morphological Closing
          ↓
Dilation
          ↓
Gaussian Blur
          ↓
Edge Feathering
          ↓
Hand Mask Integration
          ↓
Final Mask
```

This helps reduce:

* Jagged edges
* Small holes
* Missing hand regions
* Hard transitions
* Segmentation artifacts
* Visible halos

---

## 💡 Lighting Compensation

The captured background and live frame may have different brightness levels because of automatic camera exposure.

The project therefore supports lighting/exposure compensation.

The system can perform:

* Brightness normalization
* Contrast normalization
* Exposure matching
* Optional color correction

This helps the replaced background blend more naturally with the live frame.

Lighting compensation can be enabled or disabled from the configuration.

---

## ✨ Edge Refinement

The project supports additional mask refinement to create smoother boundaries around the person.

Processing includes:

* Morphological closing
* Dilation
* Gaussian smoothing
* Mask feathering
* Optional edge refinement

This reduces harsh or jagged edges around the person's silhouette.

---

## 🎬 Video Recording

The processed ghost effect can optionally be recorded.

Press:

```text
R
```

to start recording.

Press `R` again to stop.

Recorded videos are saved inside:

```text
output/
```

The HUD displays:

```text
● REC
```

while recording is active.

---

## 📊 Real-Time HUD

The application displays useful information directly on the camera feed.

Example:

```text
┌──────────────────────────────────┐
│ 👻 GHOST INVISIBILITY            │
│                                  │
│ Camera:       ON                 │
│ Background:   READY              │
│ Ghost:        78%                │
│ FPS:          29.4               │
│ Gesture:      READY              │
│ Recording:    OFF                │
└──────────────────────────────────┘
```

During background capture:

```text
┌──────────────────────────────────┐
│       CAPTURING BACKGROUND       │
│                                  │
│ ███████████████░░░░░             │
│ 72 / 90                           │
└──────────────────────────────────┘
```

---

## ⚙️ Configuration

Important parameters are centralized in the configuration module.

Example:

```python
CAMERA_INDEX = 0

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

BACKGROUND_CAPTURE_FRAMES = 90

SEGMENTATION_THRESHOLD = 0.25
MORPH_KERNEL = 9
DILATION_ITERATIONS = 1
GAUSSIAN_BLUR = 3
MASK_MULTIPLIER = 0.9

HAND_KERNEL = 15
HAND_DILATION = 2

PINCH_THRESHOLD = 0.06

ALPHA_SPEED = 0.10

ENABLE_LIGHTING_COMPENSATION = True
ENABLE_EDGE_REFINEMENT = True
ENABLE_TWO_HAND_GESTURE = False
```

These values can be tuned according to the camera, lighting conditions, and system performance.

---

## 🎮 Controls

| Control                     | Action                       |
| --------------------------- | ---------------------------- |
| `Space`                     | Capture background           |
| Thumb + Middle Finger Pinch | Toggle Ghost Mode            |
| `R`                         | Start/Stop recording         |
| `T`                         | Toggle two-hand gesture mode |
| `H`                         | Show/Hide HUD                |
| `L`                         | Toggle lighting compensation |
| `E`                         | Toggle edge refinement       |
| `Esc`                       | Exit                         |

---

## 🛠️ Tech Stack

| Technology    | Purpose                                      |
| ------------- | -------------------------------------------- |
| **Python**    | Core application                             |
| **OpenCV**    | Webcam, image processing and video recording |
| **MediaPipe** | Person segmentation and hand tracking        |
| **NumPy**     | Numerical operations and image compositing   |

---

## 📁 Project Structure

```text
Ghost_Invisibility/
│
├── src/
│   ├── main.py
│   ├── engine.py
│   ├── camera.py
│   ├── segmentation.py
│   ├── hands.py
│   ├── gestures.py
│   ├── background.py
│   ├── compositing.py
│   ├── lighting.py
│   ├── recorder.py
│   ├── hud.py
│   └── config.py
│
├── assets/
│   └── demo-placeholder.txt
│
├── output/
│   └── .gitkeep
│
├── .gitignore
├── LICENSE
├── README.md
├── RUN.md
└── requirements.txt
```

---

## 📋 Requirements

* Python **3.9+**
* Working webcam
* Windows, Linux, or macOS
* Internet connection only for initial dependency installation
* Sufficient CPU performance for real-time MediaPipe processing

---

## 🚀 Installation

Clone the repository:

```bash
git clone <your-repository-url>
cd Ghost_Invisibility
```

Create a virtual environment:

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Run

From the project root:

```bash
python src/main.py
```

### Basic Workflow

```text
1. Start the application
        ↓
2. Move out of the camera frame
        ↓
3. Press Space
        ↓
4. Wait for background capture
        ↓
5. Enter the camera frame
        ↓
6. Pinch thumb + middle finger
        ↓
7. Become invisible 👻
```

---

## 📈 Performance

Performance depends on:

* Camera resolution
* CPU performance
* MediaPipe processing speed
* Lighting conditions
* Background complexity
* Enabled processing features

For better FPS:

* Reduce camera resolution.
* Disable edge refinement.
* Disable two-hand gesture mode.
* Reduce unnecessary processing.
* Use a stable lighting environment.

The current FPS is displayed in the HUD.

---

## ⚠️ Limitations

The effect works best when:

* The camera remains fixed.
* The background is mostly static.
* Lighting remains relatively consistent.
* The person is separated from the background.
* The webcam provides a reasonably clear image.

This is not physical invisibility. The effect is created through **computer vision-based person segmentation and background replacement**.

---

## 🔮 Future Improvements

Potential extensions include:

* [ ] AI-based segmentation refinement
* [ ] Advanced human matting
* [ ] Temporal mask stabilization
* [ ] Optical-flow-based background handling
* [ ] GPU acceleration
* [ ] Multiple-person invisibility
* [ ] Selective object invisibility
* [ ] Background image/video replacement
* [ ] Automatic scene-change detection
* [ ] Mobile deployment
* [ ] Web deployment
* [ ] Real-time streaming
* [ ] GUI-based parameter controls
* [ ] Advanced ghost visual effects

---

## 🧪 Troubleshooting

### Webcam does not open

Check that another application is not using the camera.

Try changing:

```python
CAMERA_INDEX = 0
```

to:

```python
CAMERA_INDEX = 1
```

or another available camera index.

---

### Low FPS

Try:

* Lowering camera resolution.
* Disabling edge refinement.
* Disabling two-hand gesture mode.
* Reducing processing resolution.

---

### Poor segmentation

Adjust:

```python
SEGMENTATION_THRESHOLD
```

A lower threshold may include more of the person, while a higher threshold creates a stricter mask.

Better lighting and greater separation between the person and background can also improve segmentation.

---

### Visible edges around the person

Try tuning:

```python
MORPH_KERNEL
DILATION_ITERATIONS
GAUSSIAN_BLUR
MASK_MULTIPLIER
```

You can also enable lighting compensation.

---

## 🎯 Project Objective

Ghost Invisibility demonstrates how multiple Computer Vision techniques can be combined into a single interactive real-time application.

```text
Computer Vision
      +
Image Processing
      +
Person Segmentation
      +
Hand Tracking
      +
Gesture Recognition
      +
Alpha Compositing
      +
Lighting Compensation
      +
Real-Time Optimization
      ↓
Interactive Invisibility Effect 👻
```

The project is designed to demonstrate practical applications of **OpenCV, MediaPipe, NumPy, image segmentation, gesture recognition, real-time video processing, and computer vision pipeline design**.

---

## 📜 License

This project is distributed under the license included in the repository.

---

## 👻 Demo

**Capture the background → enter the frame → pinch your fingers → disappear.**

> *The camera sees you. The algorithm doesn't.* 👻
