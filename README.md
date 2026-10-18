# Workplace Safety Sentinel

A computer vision prototype that detects people in workplace footage and records potential restricted-zone entry incidents.

## Features
- Person detection using YOLOv8
- Visual restricted-zone overlay
- Person tracking where tracking IDs are available
- JSON incident logging
- Annotated video output

## Tech Stack
- Python
- Ultralytics YOLOv8
- OpenCV
- NumPy

## Setup

Create and activate a virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

Install dependencies:

    python -m pip install -r requirements.txt

Ensure the input video is named people.mp4 and is in the project folder.

Run:

    python sentinel.py

The YOLO model weights may download automatically on the first run.

## Output
- annotated_video.mp4 — processed video with detection overlays
- incidents.json — logged potential zone-entry incidents

## Limitations
This is a hackathon prototype, not a certified safety system. Detection and alerts depend on video quality, tracking, and zone configuration. Validate all alerts before real-world use.
