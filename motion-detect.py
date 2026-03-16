#!/usr/bin/env python3
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder
import cv2
import numpy as np
import time
from datetime import datetime
import os

# ---------------------------------------------------------------------------
# Configuration — values are read from environment variables (set via .env).
# os.getenv(KEY, default) reads the variable if present, or falls back to the
# default so the script still works even without a .env file.
# ---------------------------------------------------------------------------
THRESHOLD       = int(os.getenv("THRESHOLD", 25))
MIN_AREA        = int(os.getenv("MIN_AREA", 800))
BLUR_SIZE       = int(os.getenv("BLUR_SIZE", 21))
MOTION_DURATION = int(os.getenv("MOTION_DURATION", 5))
SAVE_PHOTOS     = os.getenv("SAVE_PHOTOS", "true").lower() == "true"
SAVE_VIDEOS     = os.getenv("SAVE_VIDEOS", "true").lower() == "true"
OUTPUT_DIR      = os.getenv("OUTPUT_DIR", "motion_captures")

# Camera resolution — main stream for recording, lores for motion detection
MAIN_WIDTH   = int(os.getenv("MAIN_WIDTH", 1920))
MAIN_HEIGHT  = int(os.getenv("MAIN_HEIGHT", 1080))
LORES_WIDTH  = int(os.getenv("LORES_WIDTH", 640))
LORES_HEIGHT = int(os.getenv("LORES_HEIGHT", 480))

# Create output directories
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/photos", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/videos", exist_ok=True)

print("Initializing security camera system...")
print(f"  Threshold: {THRESHOLD}, Min area: {MIN_AREA}, Blur: {BLUR_SIZE}")
print(f"  Motion duration: {MOTION_DURATION}s | Photos: {SAVE_PHOTOS} | Videos: {SAVE_VIDEOS}")
print(f"  Main: {MAIN_WIDTH}x{MAIN_HEIGHT} | Lores: {LORES_WIDTH}x{LORES_HEIGHT}")

picam2 = Picamera2()

# Configure with both main and lores streams.
# Main is used for high-quality capture; lores is used for fast motion detection.
config = picam2.create_video_configuration(
    main={"size": (MAIN_WIDTH, MAIN_HEIGHT)},
    lores={"size": (LORES_WIDTH, LORES_HEIGHT), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()
time.sleep(2)

encoder = H264Encoder()

print(f"\nSecurity camera active. Output directory: {OUTPUT_DIR}")
print("\nMonitoring for motion...\n")

# Capture first frame to use as baseline for motion detection
frame = picam2.capture_array("lores")
previous_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
previous_gray = cv2.GaussianBlur(previous_gray, (BLUR_SIZE, BLUR_SIZE), 0)

motion_detected = False
last_motion_time = 0
recording = False
motion_event_count = 0

try:
    while True:
        # Capture low-res frame for motion detection
        frame = picam2.capture_array("lores")

        # Convert to grayscale and blur to reduce noise before comparing frames
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        gray = cv2.GaussianBlur(gray, (BLUR_SIZE, BLUR_SIZE), 0)

        # Compute the absolute difference between current and previous frame
        frame_diff = cv2.absdiff(previous_gray, gray)
        thresh = cv2.threshold(frame_diff, THRESHOLD, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        current_motion = False
        total_motion_area = 0

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > MIN_AREA:
                current_motion = True
                total_motion_area += area

        if current_motion:
            timestamp = datetime.now()

            if not motion_detected:
                motion_event_count += 1
                print(f"\n[{timestamp.strftime('%H:%M:%S')}] === MOTION EVENT #{motion_event_count} STARTED ===")
                print(f"  Motion area: {total_motion_area}")

                if SAVE_PHOTOS:
                    photo_filename = f"{OUTPUT_DIR}/photos/motion_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
                    picam2.capture_file(photo_filename, "main")
                    print(f"  Saved photo: {photo_filename}")

                if SAVE_VIDEOS and not recording:
                    video_filename = f"{OUTPUT_DIR}/videos/motion_{timestamp.strftime('%Y%m%d_%H%M%S')}.h264"
                    picam2.start_encoder(encoder, output=video_filename)
                    recording = True
                    print(f"  Started recording: {video_filename}")

            motion_detected = True
            last_motion_time = time.time()

        else:
            if motion_detected:
                time_since_motion = time.time() - last_motion_time

                if time_since_motion > MOTION_DURATION:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Motion event ended")

                    if recording:
                        picam2.stop_encoder()
                        recording = False
                        print("  Stopped recording")

                    print("Resuming monitoring...\n")
                    motion_detected = False

        previous_gray = gray
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\n\nShutting down security camera...")

    if recording:
        picam2.stop_encoder()

    picam2.stop()

    print(f"\nSession summary:")
    print(f"  Motion events detected: {motion_event_count}")
    print(f"  Files saved in: {OUTPUT_DIR}/")