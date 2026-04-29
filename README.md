# Unified Overnight Research Orchestrator

## Overview

This repository contains the complete unified overnight research system for the Gematria project. It orchestrates autonomous web research, pattern analysis, and knowledge synthesis to generate actionable intelligence reports.

## Structure

```
unified_overnight_research/
├── database/          # SQLite database for storing observations
├── domain/            # Domain data storage
├── forces/            # Force definitions and data
├── symbols/           # Symbol definitions
├── obsidian_exports/  # Exported knowledge graph nodes
├── logs/              # Operational logs
├── OUR/               # Image-based research data
├── reports/           # Generated reports
├── research/          # Raw research output
├── scripts/           # Utility scripts
├── templates/         # Report templates
├── observations/      # Live observation data
├── composer.py        # Main composition engine
├── unified_engine.py  # Core orchestration logic
├── loop_runner.py     # Loop execution controller
└── README.md          # This file
```

## Usage

### Running the Overnight Research Loop

**Quick start:**
```bash
cd ~/.hermes/gematria/unified_overnight_research
./run_unified.sh
```

**Using composer.py directly:**
```bash
python3 composer.py --config config.yaml
```

### Configuration

Edit `composer.py` or create a `config.yaml` in the root directory to customize:
- Database path
- Observation storage locations
- Report templates
- Webhook endpoints

## Reports Generated

1. **FINAL_OVERNIGHT_REPORT.md** - Main synthesis report with findings and recommendations
2. **FINAL_OVERNIGHT_STATUS.md** - Status summary of research activities
3. **STATUS_REPORT.md** - Detailed operational status
4. **GEMATRIA_UNIFIED_OVERNIGHT.md** - Gematria-specific overnight analysis

## Key Components

- **composer.py**: Main entry point for orchestrating overnight research
- **unified_engine.py**: Core orchestration logic for multi-agent research
- **loop_runner.py**: Manages research loop execution and state
- **create_correlation_matrix.py**: Generates correlation matrices from observations

## Requirements

- Python 3.8+
- Firecrawl API (configured via environment variables)
- SearXNG or DuckDuckGo for local search fallbacks

## License

MIT
