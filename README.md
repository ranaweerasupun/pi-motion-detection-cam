# Raspberry Pi Motion Detection Security Camera

A motion-detection security camera system built for the Raspberry Pi. The camera runs continuously, comparing frames to detect movement, and saves timestamped photos and H264 video clips whenever a motion event is triggered.

---

## Features

- Frame-differencing motion detection with configurable sensitivity
- Dual-stream capture — low-res stream for detection, high-res for recording
- Saves timestamped photos (`.jpg`) and video clips (`.h264`) on motion events
- All parameters tunable via `.env` without touching the source code
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

Press `Ctrl+C` to stop. A session summary is printed on exit.

---

## Configuration

All settings are controlled through a `.env` file — the source code never needs to be edited directly. This also keeps any sensitive values (such as API keys if cloud backup or alerting is added later) out of version control.

**Setup:**

```bash
cp env.example .env
# Then open .env and adjust values as needed
```

| Variable               | Default           | Description                                                 |
|------------------------|-------------------|-------------------------------------------------------------|
| `THRESHOLD`            | `25`              | Pixel intensity change (0–255) to count as motion           |
| `MIN_AREA`             | `800`             | Minimum contour area (px²) to trigger a motion event        |
| `BLUR_SIZE`            | `21`              | Gaussian blur kernel — higher means less sensitive to noise |
| `MOTION_DURATION`      | `5`               | Seconds to keep recording after motion stops                |
| `SAVE_PHOTOS`          | `true`            | Save a photo at the start of each motion event              |
| `SAVE_VIDEOS`          | `true`            | Record an H264 video clip during each motion event          |
| `OUTPUT_DIR`           | `motion_captures` | Root folder for saved files                                 |
| `MAIN_WIDTH/HEIGHT`    | `1920x1080`       | Resolution for photo and video capture                      |
| `LORES_WIDTH/HEIGHT`   | `640x480`         | Resolution used for motion detection processing             |

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

## Working Mechanism...

1. A low-resolution (640×480) RGB stream runs continuously for motion analysis.
2. Each frame is converted to grayscale and blurred to reduce noise.
3. The absolute difference between the current and previous frame is thresholded and dilated.
4. Contours are extracted — if any exceed `MIN_AREA`, a motion event is triggered.
5. A full-resolution (1920×1080) photo is saved and H264 video recording begins.
6. Recording continues until no motion has been detected for `MOTION_DURATION` seconds.

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

Captured photos and videos are saved to `./motion_captures/` on the host machine.

### Notes
- The container runs with `--privileged` to allow camera hardware access via `libcamera`.
- If `/dev/video0` is not recognised, check available devices with `ls /dev/video*` on the Pi and update `docker-compose.yml` accordingly.
- Built for **ARM64** (Raspberry Pi 3/4/5). Building on an x86 machine requires QEMU or Docker Buildx for cross-compilation.

---

## License

MIT License — free to use, modify, and distribute.
