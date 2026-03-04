#!/usr/bin/env python3
# the fixed motion_security_camera.py code
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder
import cv2
import numpy as np
import time
from datetime import datetime
import os

# Configuration
THRESHOLD = 25
MIN_AREA = 800
BLUR_SIZE = 21
MOTION_DURATION = 5  # Seconds to record after motion stops
OUTPUT_DIR = "motion_captures"
SAVE_PHOTOS = True
SAVE_VIDEOS = True

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/photos", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/videos", exist_ok=True)

print("Initializing security camera system...")
picam2 = Picamera2()

# Configure with both main and lores streams
# Main for high-quality capture, lores for fast motion detection
# FIX: Explicitly set lores format to RGB888 to avoid YUV420 conversion issues
config = picam2.create_video_configuration(
    main={"size": (1920, 1080)},  # High quality for recording
    lores={"size": (640, 480), "format": "RGB888"}     # Low res for motion detection in RGB
)
picam2.configure(config)
picam2.start()
time.sleep(2)

# Setup for video recording
encoder = H264Encoder()

print("Security camera active...")
print(f"Output directory: {OUTPUT_DIR}")
print(f"Threshold: {THRESHOLD}, Min area: {MIN_AREA}")
print("\nMonitoring for motion...\n")

# Initialize motion detection
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
        
        # Process for motion detection
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        gray = cv2.GaussianBlur(gray, (BLUR_SIZE, BLUR_SIZE), 0)
        
        frame_diff = cv2.absdiff(previous_gray, gray)
        thresh = cv2.threshold(frame_diff, THRESHOLD, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Check for motion
        current_motion = False
        total_motion_area = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > MIN_AREA:
                current_motion = True
                total_motion_area += area
        
        # Handle motion detection
        if current_motion:
            timestamp = datetime.now()
            
            if not motion_detected:
                # Motion just started
                motion_event_count += 1
                print(f"\n[{timestamp.strftime('%H:%M:%S')}] === MOTION EVENT #{motion_event_count} STARTED ===")
                print(f"Motion area: {total_motion_area}")
                
                # Save photo
                if SAVE_PHOTOS:
                    photo_filename = f"{OUTPUT_DIR}/photos/motion_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
                    picam2.capture_file(photo_filename, "main")
                    print(f"Saved photo: {photo_filename}")
                
                # Start recording video
                if SAVE_VIDEOS and not recording:
                    video_filename = f"{OUTPUT_DIR}/videos/motion_{timestamp.strftime('%Y%m%d_%H%M%S')}.h264"
                    picam2.start_encoder(encoder, output=video_filename)
                    recording = True
                    print(f"Started recording: {video_filename}")
            
            motion_detected = True
            last_motion_time = time.time()
        
        else:
            # No motion detected
            if motion_detected:
                # Check if motion just stopped
                time_since_motion = time.time() - last_motion_time
                
                if time_since_motion > MOTION_DURATION:
                    # Motion event ended
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Motion event ended")
                    
                    if recording:
                        picam2.stop_encoder()
                        recording = False
                        print("Stopped recording")
                    
                    print("Resuming monitoring...\n")
                    motion_detected = False
        
        # Update previous frame
        previous_gray = gray
        
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\n\nShutting down security camera...")
    
    if recording:
        picam2.stop_encoder()
    
    picam2.stop()
    
    print(f"\nSession summary:")
    print(f"Motion events detected: {motion_event_count}")
    print(f"Files saved in: {OUTPUT_DIR}/")