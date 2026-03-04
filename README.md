# 🎥 Raspberry Pi Motion Detection Security Camera

A lightweight motion-detection security camera system built for the Raspberry Pi. It continuously monitors a camera feed and automatically saves photos and H264 video clips whenever motion is detected.

---

## Features

- Real-time motion detection using frame differencing
- Dual-stream capture — low-res stream for fast detection, high-res for recording
- Saves timestamped photos (`.jpg`) and video clips (`.h264`) on motion events
- Configurable sensitivity, minimum motion area, and post-motion recording duration
- Clean session summary on shutdown

---

## Requirements

### Hardware
- Raspberry Pi (3, 4, or 5 recommended)
- Raspberry Pi Camera Module (v2, v3, or HQ)

### Software
- Python 3.7+
- [Picamera2](https://github.com/raspberrypi/picamera2)
- OpenCV (`cv2`)
- NumPy

---

## Installation

```bash
# Clone the repository
git clone https://github.com/ranaweerasupun/pi-motion-detection-cam.git
cd pi-motion-detection-cam

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install opencv-python numpy
sudo apt install -y python3-picamera2
```

> **Note:** `picamera2` is best installed via `apt` on Raspberry Pi OS, not `pip`.

---

## Usage

```bash
python3 motion-detect.py
```

Press `Ctrl+C` to stop. A session summary will be printed on exit.

---

## Configuration

All settings are controlled through a `.env` file — you never need to edit the source code directly. This also keeps any sensitive values (like passwords or API keys if you add alerts or cloud backup) out of version control.

**Setup:**

```bash
cp env.example .env
# Then open .env and adjust values to your liking
```

| Variable          | Default       | Description                                                    |
|-------------------|---------------|----------------------------------------------------------------|
| `THRESHOLD`       | `25`          | Pixel intensity change (0–255) to count as motion              |
| `MIN_AREA`        | `800`         | Minimum contour area (px²) to trigger a motion event           |
| `BLUR_SIZE`       | `21`          | Gaussian blur kernel — higher means less sensitive to noise    |
| `MOTION_DURATION` | `5`           | Seconds to keep recording after motion stops                   |
| `SAVE_PHOTOS`     | `true`        | Save a photo at the start of each motion event                 |
| `SAVE_VIDEOS`     | `true`        | Record an H264 video clip during each motion event             |
| `OUTPUT_DIR`      | `motion_captures` | Root folder for saved files                               |
| `MAIN_WIDTH/HEIGHT` | `1920x1080` | Resolution for photo and video capture                         |
| `LORES_WIDTH/HEIGHT` | `640x480`  | Resolution for motion detection processing                     |


---

## Output Structure

```
motion_captures/
├── photos/
│   └── motion_20240315_143022.jpg
└── videos/
    └── motion_20240315_143022.h264
```

---

## How It Works

1. A low-resolution (640×480) RGB stream is captured continuously for motion analysis.
2. Each frame is converted to grayscale and blurred to reduce noise.
3. The absolute difference between the current and previous frame is thresholded and dilated.
4. Contours are found — if any exceed `MIN_AREA`, a motion event is triggered.
5. A full-resolution (1920×1080) photo is saved and H264 video recording begins.
6. Recording continues until no motion is detected for `MOTION_DURATION` seconds.

---

## Docker

### Build & Run

```bash
# Build the image
docker compose build

# Start the camera (runs in background)
docker compose up -d

# View live logs
docker compose logs -f

# Stop the camera
docker compose down
```

Captured photos and videos are saved to `./motion_captures/` on your host machine.

### Notes
- The container runs with `--privileged` to allow camera hardware access via `libcamera`.
- If `/dev/video0` is not recognised, check available devices with `ls /dev/video*` on your Pi and update `docker-compose.yml` accordingly.
- Built for **ARM64** (Raspberry Pi 3/4/5). If building on an x86 machine for cross-compilation, you will need QEMU or Docker Buildx.

---

## License

MIT License — feel free to use, modify, and distribute.
