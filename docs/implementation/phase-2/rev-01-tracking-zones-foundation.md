# Phase 2 Revision 1: Tracking and Zones Foundation

## Overview

Phase 2 Rev 1 adds **object tracking** and **rectangular zone evaluation** on top of the existing Phase 1 detection pipeline. It does NOT implement bottle pickup inference or event generation - those come in later revisions.

### Key Components Added

| Component | Purpose |
|-----------|---------|
| `Zone` model | Rectangular region with name, coordinates, point/bbox containment checks |
| `Track` model | Tracked object with ID, class, bbox history, age, hit streak, zone events |
| `ZoneLoader` | Loads zone definitions from config (`detection.zones`) |
| `ZoneManager` | Evaluates which zones contain a detection/track bbox center |
| `SimpleTracker` | Class-aware centroid tracker (distance + class matching, confirmation logic) |
| `ZoneRenderer` | Draws zones, detections, track IDs on frames for visual verification |
| `run_tracking.py` | End-to-end script: camera → detection → tracking → zones → annotated output |

---

## Data Flow Diagram

```mermaid
flowchart TD
    A[RTSP Camera Stream] --> B[CameraPipeline]
    B --> C[FrameProcessor callback per frame]
    C --> D{Every N frames?}
    D -->|No| E[Skip detection]
    D -->|Yes| F[YOLO Detector]
    F --> G[Confidence Filter]
    G --> H[Class Filter person/bottle]
    H --> I[SimpleTracker.update]
    I --> J[Match to existing tracks\nby class + distance]
    I --> K[Create new tracks\nfor unmatched]
    I --> L[Age out stale tracks]
    J --> M[Active Tracks]
    K --> M
    L --> M
    M --> N[ZoneManager.evaluate_track]
    N --> O{Track in zone?}
    O -->|bottle_home| P[bottle_home_hits++]
    O -->|desk| Q[desk_hits++]
    M --> R[ZoneRenderer.save_frame]
    P --> R
    Q --> R
    R --> S[artifacts/tracking/session/frame_XXXXXX.jpg]
    E --> T[Next frame]
    S --> T
```

---

## Frame Processing Pipeline

```mermaid
sequenceDiagram
    participant Camera as CameraPipeline
    participant Processor as TrackingProcessor
    participant Detector as YoloDetector
    participant Tracker as SimpleTracker
    participant Zones as ZoneManager
    participant Renderer as ZoneRenderer
    participant Output as Disk

    loop For each frame
        Camera->>Processor: frame (via frame_processor callback)
        alt Detection frame (frame_id % N == 0)
            Processor->>Detector: detect(frame)
            Detector-->>Processor: list[Detection]
            Processor->>Detector: filter by confidence
            Processor->>Detector: filter by class (person/bottle)
            Processor->>Tracker: update(filtered_detections)
            Tracker->>Tracker: mark all existing tracks missed
            Tracker->>Tracker: group detections by class
            Tracker->>Tracker: match detections to tracks (min distance)
            Tracker->>Tracker: create new tracks for unmatched
            Tracker->>Tracker: remove tracks with missed_frames > max_missed
            Tracker-->>Processor: list[Track] (confirmed only)
            Processor->>Zones: evaluate_track(track)
            Zones-->>Processor: list[zone_names]
            Processor->>Processor: increment zone hit counters
            Processor->>Renderer: save_frame(frame, detections, tracks, zones)
            Renderer->>Renderer: draw zones (rectangles + labels)
            Renderer->>Renderer: draw detection boxes + confidence
            Renderer->>Renderer: draw track IDs + age
            Renderer->>Output: artifacts/tracking/session/frame_XXXXXX.jpg
        else
            Processor->>Camera: return (no processing)
        end
    end
```

---

## SimpleTracker Matching Logic

```mermaid
flowchart TD
    A[update(detections)] --> B[Mark all tracks missed]
    B --> C[Group detections by class_name]
    C --> D{For each class}
    D --> E[Get existing tracks of same class]
    E --> F{Any existing tracks?}
    F -- No --> G[Create new track for each detection]
    F -- Yes --> H[Build cost matrix: Euclidean distance between bbox centers]
    H --> I[Greedy assignment: sort pairs by distance]
    I --> J{For each pair by distance}
    J --> K{distance <= max_distance?}
    K -- Yes --> L[Update matched track with detection]
    K -- No --> M[Skip - too far]
    J --> N{All pairs processed?}
    N -- More --> J
    N -- Done --> O[Create new tracks for unmatched detections]
    O --> P[Remove tracks with missed_frames > max_missed_frames]
    P --> Q[Return confirmed tracks only (hit_streak >= min_hits)]
```

---

## Zone Evaluation

```mermaid
flowchart LR
    A[Track.bbox] --> B[ZoneManager.evaluate_track]
    B --> C[For each zone]
    C --> D{zone.contains_bbox_center(bbox)?}
    D -- Yes --> E[Add zone.name to result]
    D -- No --> F[Skip]
    E --> G[Next zone]
    F --> G
    G --> H{More zones?}
    H -- Yes --> C
    H -- No --> I[Return list[zone_names]]
```

---

## Artifact Output Structure

```
artifacts/
├── frames/                 │
 └── tracking/              # NEW in Phase 2 Rev1
     └── jetson-session/
         ├── frame_000030.jpg  # Detection frame 0: zones + detections + track IDs
         ├── frame_000060.jpg  # Detection frame 1: tracks aged, new matches
         ├── frame_000090.jpg  # Detection frame 2: ...
         └── ...
```

### What You See in Annotated Frames

- **Green rectangle + label**: `bottle_home` zone
- **Blue rectangle + label**: `desk` zone  
- **Red boxes + "person 0.XX"**: Person detections
- **Green boxes + "bottle 0.XX"**: Bottle detections
- **"ID:1 (age:5)"**: Track ID and age above detection box

---

## Configuration (jetson.yaml)

```yaml
detection:
  enabled: true
  model_name: yolov8n.pt
  confidence_threshold: 0.35
  classes: [person, bottle]
  run_every_n_frames: 30
  output_dir: artifacts/detections
  zones:                           # NEW
    - name: bottle_home
      type: rectangle
      x1: 500; y1: 400; x2: 850; y2: 720
    - name: desk
      type: rectangle
      x1: 250; y1: 300; x2: 1200; y2: 720

tracking:
  enabled: true
  output_dir: artifacts/tracking
  max_missed_frames: 30
  match_distance_threshold: 100.0
```

---

## Running It

```bash
# Export your Tapo RTSP URL
export TAPO_RTSP_URL='rtsp://sightloop:LetsCreateAwesome$*@192.168.50.207:554/stream1'

# Run tracking for 300 frames
uv run python scripts/run_tracking.py --config configs/jetson.yaml --max-frames 300
```

### Expected Output

```json
{
  "frames_processed": 300,
  "detection_frames_processed": 10,
  "total_tracks_created": 12,
  "active_tracks": 3,
  "bottle_tracks": 8,
  "person_tracks": 4,
  "bottle_home_zone_hits": 25,
  "desk_zone_hits": 45,
  "annotated_output_dir": "artifacts/tracking/jetson-session"
}
```

---

## What's NOT in This Revision

| Feature | Status |
|---------|--------|
| Bottle pickup inference | Phase 2 Rev 2+ |
| Event database/alerts | Phase 3 |
| Posture analysis | Phase 3 |
| LLM reasoning | Phase 3 |
| Automatic zone selection | Manual via annotated frames |
| Multi-camera | Future |

---

## Tuning Zones

1. Run tracking: `uv run python scripts/run_tracking.py ... --max-frames 300`
2. Review frames in `artifacts/tracking/jetson-session/`
3. Adjust `x1,y1,x2,y2` in `configs/jetson.yaml` under `detection.zones`
4. Re-run to verify

The placeholder zones in `jetson.yaml` are intentionally rough - you tune them by looking at the annotated output.