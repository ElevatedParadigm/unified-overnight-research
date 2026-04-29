# Unified Overnight Research Engine - Steve's Gematria

## Overview
Single comprehensive script that combines:
- **Web Scraping** (SearXNG standalone mode)
- **Pattern Analysis** (cross-domain convergence detection)
- **Relationship Iteration** (discovering connections between new discoveries)
- **Temporal Tracking** (symbol appearances across domains over time)
- **Report Generation** (markdown analysis with ASCII visualizations)

## Location
`/home/avalonas/.hermes/gematria/unified_overnight_research/`

## Architecture
```
┌─────────────────────────────────────┐
│   Overnight Runner                  │
│         (Bash)                      │
└──────────────┬──────────────────────┘
               ↓
    ┌───────────────────────────────┐
    │  Unified Engine Python        │
    │  - Queries → Scrape → Analyze │
    │  - Cross-domain convergence    │
    │  - Relationship iteration      │
    │  - Temporal tracking           │
    │  - Full report generation      │
    └───────────────────────────────┘
```

## Features (vs. Split Approach)
- ✅ **Single dependency** - no inter-script coordination needed
- ✅ **Atomic execution** - all-or-nothing with proper cleanup
- ✅ **Simpler cron setup** - one entry point
- ✅ **Easier debugging** - single place to trace issues
- ✅ **Complete state management** - handles database updates atomically
- ⚠️ **Less flexible** - harder to swap components independently

## Files
1. `unified_engine.py` (main Python script, ~250 lines)
2. `run_unified.sh` (Bash wrapper with logging)
3. `README.md` (this documentation)
4. Template reports in `reports/`

## Key Capabilities
- **Pattern Analysis**: Detects convergence across geographic/military/elemental domains
- **Relationship Iteration**: Finds connections between newly discovered entities
- **Cross-Domain Detection**: Identifies symbols appearing unexpectedly in different contexts
- **Temporal Tracking**: Logs symbol frequency and evolution over time
- **ASCII Heatmaps**: Terminal-compatible visualizations of relationship density

## Execution
```bash
cd /home/avalonas/.hermes/gematria/unified_overnight_research
chmod +x run_unified.sh
./run_unified.sh
```

## Cron Installation
```bash
echo "0 3 * * * cd /home/avalonas/.hermes/gematria/unified_overnight_research && ./run_unified.sh >> /home/avalonas/.hermes/gematria/cron_logs/unified_overnight.log 2>&1" | crontab -
```

---

*Note: After creation, modular_analysis will be built for comparison and experimentation.*