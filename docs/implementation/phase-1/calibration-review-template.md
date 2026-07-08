# Calibration Review Template

Use this template to review calibration frames captured for Phase 2 zone setup.

## Session Information

- **Session Name:** `{session_name}`
- **Position Label:** `{position_label}` (e.g., desk-front-angle, desk-top-angle, desk-evening-light)
- **Camera Source:** `{camera_source_masked}`
- **Resolution:** `{resolution}`
- **Lighting Condition:** (e.g., morning natural, office fluorescent, evening lamp)
- **Date/Time:** `{created_at}`

## Frame Quality Checklist

| Check | Pass/Fail | Notes |
|-------|-----------|-------|
| Bottle visible at rest position? | | |
| Bottle visible when picked up? | | |
| Desk surface visible? | | |
| Upper body / torso visible? | | |
| No significant glare/reflection on bottle? | | |
| No motion blur on key frames? | | |
| Consistent lighting across frames? | | |

## Frame Coverage

- **Total frames saved:** `{frames_saved}`
- **Save interval:** Every `{save_every_n_frames}` frames
- **Max frames requested:** `{max_frames}`

## Recommended for Phase 2 Zones?

- [ ] Yes - good candidate for bottle_home zone
- [ ] Yes - good candidate for desk zone
- [ ] Yes - good candidate for person zone
- [ ] No - poor visibility / lighting issues
- [ ] Needs re-capture with different position

## Candidate Zone Rectangles (optional, for manual review)

| Zone | x1, y1, x2, y2 | Confidence | Notes |
|------|----------------|------------|-------|
| bottle_home | | | |
| desk | | | |
| person | | | |

## Notes

```
{notes}
```

## Manifest Reference

See: `artifacts/calibration/{session_name}/manifest.json`