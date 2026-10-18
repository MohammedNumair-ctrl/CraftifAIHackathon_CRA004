

import cv2
import json
import time
from pathlib import Path
from datetime import datetime
from ultralytics import YOLO

# All files are stored beside this script
BASE_DIR = Path(__file__).resolve().parent
VIDEO_PATH = BASE_DIR / "people.mp4"
OUTPUT_PATH = BASE_DIR / "annotated_video.mp4"
INCIDENTS_PATH = BASE_DIR / "incidents.json"

# Restricted zone coordinates as percentages of video width/height.
# Adjust these after seeing the video.
ZONE = [
    (0.55, 0.25),
    (0.95, 0.25),
    (0.95, 0.95),
    (0.55, 0.95),
]

CONFIDENCE = 0.35
MODEL_NAME = "yolov8n.pt"
PROCESS_EVERY_N_FRAMES = 1


def main():
    if not VIDEO_PATH.exists():
        raise FileNotFoundError(
            f"Video not found: {VIDEO_PATH}\n"
            "Place people.mp4 beside sentinel.py."
        )

    print("Loading YOLO model...")
    model = YOLO(MODEL_NAME)

    cap = cv2.VideoCapture(str(VIDEO_PATH))
    if not cap.isOpened():
        raise RuntimeError("Could not open people.mp4")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Process at a smaller resolution for CPU performance.
    scale = min(1.0, 960 / width)
    out_width = max(2, int(width * scale) // 2 * 2)
    out_height = max(2, int(height * scale) // 2 * 2)

    zone_points = [
        (int(x * out_width), int(y * out_height))
        for x, y in ZONE
    ]

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(
        str(OUTPUT_PATH), fourcc, fps,
        (out_width, out_height)
    )

    if not writer.isOpened():
        cap.release()
        raise RuntimeError("Could not create output video.")

    incidents = []
    active_ids = set()
    frame_number = 0
    start_time = time.time()

    print(f"Input: {VIDEO_PATH.name}")
    print(f"Resolution: {out_width}x{out_height}")
    print("Running on CPU. Press Q in the video window to stop.")
    print("If the preview is slow, let it continue processing.")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            frame_number += 1
            frame = cv2.resize(frame, (out_width, out_height))

            # Run person detection and tracking on CPU.
            if frame_number % PROCESS_EVERY_N_FRAMES == 0:
                results = model.track(
                    frame,
                    persist=True,
                    classes=[0],
                    conf=CONFIDENCE,
                    imgsz=640,
                    device="cpu",
                    verbose=False,
                    tracker="bytetrack.yaml"
                )

                result = results[0]
                current_ids = set()
                inside_count = 0

                if result.boxes is not None:
                    boxes = result.boxes
                    coords = boxes.xyxy.cpu().numpy()
                    ids = (
                        boxes.id.int().cpu().tolist()
                        if boxes.id is not None
                        else [None] * len(coords)
                    )
                    confs = boxes.conf.cpu().tolist()

                    for box, track_id, confidence in zip(
                        coords, ids, confs
                    ):
                        x1, y1, x2, y2 = map(int, box)
                        # Use the bottom-centre point to estimate
                        # where the person stands on the ground.
                        foot = ((x1 + x2) // 2, y2)

                        inside = cv2.pointPolygonTest(
                            __import__("numpy").array(
                                zone_points, dtype="int32"
                            ),
                            foot,
                            False
                        ) >= 0

                        if track_id is not None:
                            current_ids.add(track_id)

                        color = (0, 220, 0)
                        label = f"Person {confidence:.2f}"

                        if inside:
                            inside_count += 1
                            color = (0, 0, 255)
                            label = "ZONE ALERT"

                            # Log only when a tracked person first
                            # enters the zone.
                            if (
                                track_id is not None
                                and track_id not in active_ids
                            ):
                                incidents.append({
                                    "incident_id": len(incidents) + 1,
                                    "timestamp": round(
                                        frame_number / fps, 2
                                    ),
                                    "recorded_at": datetime.now().isoformat(
                                        timespec="seconds"
                                    ),
                                    "event": "person_in_restricted_zone",
                                    "track_id": track_id,
                                    "confidence": round(
                                        float(confidence), 3
                                    ),
                                    "zone": "restricted_zone"
                                })
                                print(
                                    f"[ALERT] Person {track_id} "
                                    f"in restricted zone at "
                                    f"{frame_number / fps:.1f}s"
                                )

                        cv2.rectangle(
                            frame, (x1, y1), (x2, y2), color, 2
                        )
                        cv2.putText(
                            frame, label, (x1, max(20, y1 - 8)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                            color, 2
                        )
                        cv2.circle(
                            frame, foot, 5, color, -1
                        )

                # Update active tracks so a later re-entry can
                # generate another incident.
                active_ids = current_ids

            # Draw the restricted zone and status overlay.
            import numpy as np
            polygon = np.array(zone_points, dtype=np.int32)
            overlay = frame.copy()
            cv2.fillPoly(overlay, [polygon], (0, 0, 180))
            frame = cv2.addWeighted(overlay, 0.18, frame, 0.82, 0)
            cv2.polylines(
                frame, [polygon], True, (0, 0, 255), 3
            )

            cv2.putText(
                frame, "RESTRICTED ZONE", (zone_points[0][0] + 5,
                                           zone_points[0][1] + 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2
            )
            cv2.putText(
                frame, f"Frames: {frame_number}/{total_frames}",
                (15, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.65, (255, 255, 255), 2
            )
            cv2.putText(
                frame, f"Incidents logged: {len(incidents)}",
                (15, 58), cv2.FONT_HERSHEY_SIMPLEX,
                0.65, (0, 0, 255), 2
            )

            writer.write(frame)

            # Preview is useful for a live demonstration.
            cv2.imshow("Workplace Safety Sentinel - Press Q to quit",
                       frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("Preview stopped by user.")
                break

            if frame_number % 100 == 0:
                elapsed = time.time() - start_time
                print(
                    f"Processed {frame_number}/{total_frames} "
                    f"frames in {elapsed:.1f}s"
                )

    finally:
        cap.release()
        writer.release()
        cv2.destroyAllWindows()

        INCIDENTS_PATH.write_text(
            json.dumps(incidents, indent=2),
            encoding="utf-8"
        )

        print("\nProcessing finished.")
        print(f"Incidents recorded: {len(incidents)}")
        print(f"Annotated video: {OUTPUT_PATH}")
        print(f"Incident log: {INCIDENTS_PATH}")


if __name__ == "__main__":
    main()
