# Automated Overnight Research Push to Tolaria

## System Overview

This directory contains an automated overnight research pipeline that pushes analysis results from cultural, military/ geopolitical, and geographic pattern studies to Tolaria via Discord webhook.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  unified_overnight_research/                                │
│    └── reports/                                              │
│          ├── cultural_patterns/                             │
│          │   ├── geographic_cultural_analysis.md            │
│          │   ├── religious_eschatological_analysis.md       │
│          │   └── mythological_symbolic_structure.md         │
│          ├── military_geopolitical_analysis/                │
│          │   ├── military_geopolitical_analysis.md           │
│          │   └── territorial_control_conflict_pattern.md     │
│          └── geographic_map_overlays_frequency_analysis/    │
│              └── geographic_map_overlays_frequency_analysis.md  │
│                                                              │
│  Cron Job: push-research-results-to-tolaria (job_id: 53482) │
│    ├── Terminal skill for file reading                      │
│    ├── Web skill for webhook posting                        │
│    └── Schedule: every 2h (demonstration mode)              │
└─────────────────────────────────────────────────────────────┘
```

---

## Cron Job Configuration

### Current Job Details:
- **Job ID:** `5348236ae4f9`
- **Name:** `push-research-results-to-tolaria`
- **Schedule:** Every 2 hours (demonstration mode)
- **Next Run:** ~14:46 UTC daily
- **Toolsets:** Terminal, Web

### Production Schedule Recommendation:
```bash
# For 3:00 AM UTC overnight runs:
#   0 3 * * * /usr/bin/python <<EOF
#   import subprocess; subprocess.run(['curl', '-X', 'POST', ...])
# EOF
```

---

## File Contents Summary

### Cultural & Geographic Analysis (`reports/cultural_patterns/`)

| File | Focus | Key Sections |
|------|-------|--------------|
| `geographic_cultural_analysis.md` | Ancient civilizations, sacred sites | Coordinate tables, trade routes, mythological systems |
| `religious_eschatological_analysis.md` | Biblical prophecies, holy calendars | Calendar systems, sacred site latitudes, apocalypse structures |
| `mythological_symbolic_structure.md` | Universal myths, archetypes | Binary/trinary patterns, flood narratives, hero's journey |

### Military & Geopolitical Analysis (`reports/military_geopolitical_analysis/`)

| File | Focus | Key Sections |
|------|-------|--------------|
| `military_geopolitical_analysis.md` | Coup sequences, territorial control | 2024 coup analysis, base relocation patterns, hotspots |
| `territorial_control_conflict_pattern_analysis.md` | Border permeability, conflicts | High-risk zones, resource nationalization, maritime disputes |

### Geographic Mapping (`reports/geographic_map_overlays_frequency_analysis/`)

| File | Focus | Key Sections |
|------|-------|--------------|
| `geographic_map_overlays_frequency_analysis.md` | Satellite imagery, coordinate encoding | Latitude bands, point distribution, map overlay frameworks |

---

## Push Process Flow

```
[1] Cron Trigger (every 2h) → Reads reports directory
    ↓
[2] File Analysis → Extracts key findings, patterns, heatmaps
    ↓
[3] Formatting → Adds YAML frontmatter, ASCII visualizations
    ↓
[4] Webhook POST → Discord channel #tolaria-general
    ↓
[5] Acknowledgment → Delivery confirmation logged
```

---

## Example Push Output Structure

### YAML Frontmatter Template:
```yaml
---
tags: [gematria, pattern-analysis, military-geopolitical]
created_at: 2024-04-29T03:00:00Z
author: unified-research-pipeline
source: /home/avalonas/.hermes/gematria/unified_overnight_research/reports/
---
```

### ASCII Heatmap Example:
```
Correlation Intensity Map (Military-Cultural Overlap):

              Military Events          Cultural Patterns
                    ████               ░░░░
Regional Sahel     ███  ▓▓             ▒  ░░
Eastern Med        ██   ▓  ░░         ▒    ░
Central Asia       ██     ▓   ░░     ▒      
Western Europe     ████████████      ░░░░░░

Legend: █ High  ▓ Medium-High  ▒ Medium  ░ Low
```

---

## Manual Push Command

To manually trigger a research push:
```bash
cd /home/avalonas/.hermes/gematria/unified_overnight_research

# Generate summary from all reports
python << 'EOF'
import glob, markdown, datetime

files = glob.glob("reports/**/*.md", recursive=True)
for f in files:
    with open(f) as fh:
        print(f"---\nFile: {f}\n")
        content = fh.read()[:500]  # First 500 chars
        print(content.strip())
        print("---")
EOF

# Post to webhook (requires web tool access)
curl -X POST https://your-webhook-url.com/tolaria \
  -H "Content-Type: application/json" \
  -d @/home/avalonas/.hermes/gematria/unified_overnight_research/reports/summary.json
```

---

## Monitoring & Logs

### Check Job Status:
```bash
cronjob action=list
# Look for job_id: 5348236ae4f9
```

### View Latest Output:
```bash
cat ~/.hermes/cron/output/push-research-results-to-tolaria-*.txt
```

---

## Next Steps for Enhancement

1. **Add Error Handling:** Retry failed webhook posts up to 3 times
2. **Optimize Frequency:** Reduce to daily runs in production (every 2h = demo mode)
3. **Add Pattern Alerts:** Detect unusual coordinate patterns requiring immediate push
4. **Dashboard Integration:** Create HTML visualization of analysis results

---

*Last updated: $(date +%Y-%m-%d %H:%M) UTC*