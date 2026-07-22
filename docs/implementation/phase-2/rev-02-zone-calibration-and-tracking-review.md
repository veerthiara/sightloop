# Phase 2 Revision 2: Zone Calibration and Tracking Review

## Goal

Make zone calibration practical and repeatable for the fixed RTSP camera setup. This revision adds automated zone calibration reports and improved visual review tooling. **No bottle pickup inference yet.**

---

## What's New

1. **Zone Calibration Reports** - JSON + Markdown reports with zone hit statistics
2. **Improved Tracking Visualization** - Zone names shown on track labels
3. **CLI Integration** - `--write-zone-report` and `--zone-notes` flags
4. **Documentation** - Clear workflow for manual zone tuning

---

## Running Tracking with Zone Report

```bash
export TAPO_RTSP_URL='rtsp://USER:PASSWORD@CAMERA_IP:554/stream1'

uv run python scripts/run_tracking.py \
  --config configs/jetson.yaml \
  --max-frames 300 \
  --write-zone-report \
  --zone-notes "Fixed right-side desk camera. Initial zone calibration run."
```

### What This Produces

```
artifacts/
├── tracking/
│   └── jetson-session/
│       ├── frame_000030.jpg    # Annotated frames with zones + tracks
│       ├── frame_000060.jpg
│       └── ...
└── zones/
    └── jetson-session/
        ├── zone-calibration-report.json   # Machine-readable
        └── zone-calibration-report.md     # Human-readable with checklist
```

---

## Understanding the Annotated Frames

Open `artifacts/tracking/jetson-session/frame_XXXXXX.jpg` and look for:

| Visual Element | Meaning |
|----------------|---------|
| **Green rectangle** | `bottle_home` zone (where bottle rests) |
| **Blue rectangle** | `desk` zone (desk surface area) |
| **Red box + "person 0.XX"** | Person detection |
| **Green box + "bottle 0.XX"** | Bottle detection |
| **"ID:1 (age:5) bottle_home"** | Track ID=1, age=5 frames, currently in `bottle_home` zone |
| **"ID:2 (age:12) desk, bottle_home"** | Track in multiple zones |

---

## Zone Tuning Workflow

### 1. Run Initial Tracking
```bash
uv run python scripts/run_tracking.py \
  --config configs/jetson.yaml \
  --max-frames 300
```

### 2. Review Frames
```bash
# Open the latest frames
open artifacts/tracking/jetson-session/frame_*.jpg
```

Look for:
- Does the **green rectangle** (`bottle_home`) cover where the bottle actually sits?
- Does the **blue rectangle** (`desk`) cover the desk surface?
- Are tracks correctly labeled with zone names when they enter zones?

### 3. Adjust Coordinates
Edit `configs/jetson.yaml`:
```yaml
zones:
  - name: bottle_home
    type: rectangle
    x1: 550   # Adjust left edge
    y1: 420   # Adjust top edge
    x2: 900   # Adjust right edge
    y2: 750   # Adjust bottom edge
  - name: desk
    type: rectangle
    x1: 300
    y1: 320
    x2: 1250
    y2: 750
```

**Coordinate system:** Origin (0,0) at top-left. x increases right, y increases down.

### 4. Re-run and Verify
```bash
uv run python scripts/run_tracking.py \
  --config configs/jetson.yaml \
  --max-frames 300 \
  --write-zone-report
```

### 5. Check the Zone Report
Open `artifacts/zones/jetson-session/zone-calibration-report.md`:

```markdown
## Zone Hit Counts (all classes)
- **bottle_home**: 45
- **desk**: 120

## Zone Hit Counts by Class
- **bottle_home**: bottle: 40, person: 5
- **desk**: bottle: 80, person: 40

## Key Zone Metrics
- `bottle_home` hits: `45`
- `desk` hits: `120`
```

**What to look for:**
- `bottle_home` should have mostly **bottle** hits, few **person** hits
- `desk` will have both (person's arms, bottle)
- If `bottle_home` has many person hits → zone too large or includes person area

---

## Report Fields Explained

| Field | Meaning |
|-------|---------|
| `zone_hits_by_name` | Total hits per zone (all classes) |
| `zone_hits_by_class` | Hits broken down by class (person/bottle) |
| `track_count_by_class` | How many unique tracks of each class |
| `bottle_home_hits` / `desk_hits` | Quick summary counters |
| `tracks_by_class` | Active tracks at end of session |

---

## Manual Review Checklist (from report)

- [ ] Open `artifacts/tracking/{session}/` and review annotated frames
- [ ] Verify `bottle_home` zone covers the bottle rest position
- [ ] Verify `desk` zone covers the desk surface area
- [ ] Check if tracks are correctly entering/exiting zones
- [ ] Check for false positives (tracks in zones when no object present)
- [ ] Check for missed detections (object in zone but no track)
- [ ] Adjust zone coordinates in `configs/jetson.yaml` if needed
- [ ] Re-run tracking after adjustments to verify
- [ ] Document any zone changes in version control

---

## What's NOT in This Revision

| Feature | Status |
|---------|--------|
| Bottle pickup inference | Phase 2 Rev 3+ |
| Event database | Phase 3 |
| Alerts/notifications | Phase 3 |
| Posture analysis | Phase 3 |
| LLM reasoning | Future |

---

## Next Steps

After zones are tuned and validated:
1. Commit zone coordinate changes to `configs/jetson.yaml`
2. Proceed to Phase 2 Revision 3: Bottle Pickup Inference
3. State machine: `on_desk` → `in_hand` → `picked_up` → `returned`