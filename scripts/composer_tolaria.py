#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STEVE'S GEMATRIA COMPOSER - Overnight Research Script (Tolaria Edition)
Orchestrator for overnight research using local Firecrawl v1.9.0 and SearXNG-Clean

This script creates structured Tolaria notes with YAML frontmatter for:
- Core Symbols ([[CORE_SYMBOL_XXXX]])
- Elemental Forces ([[ELEMENTAL_FORCE_XXX]])
- Domain Analysis ([[DOMAIN_XXX]])
- Cross-Reference Relationships (CROSS_REF_ID)
- Research Timelines ([[RESEARCH_CYCLE_XXX]])

All notes follow unified YAML schema for Tolaria vault compatibility.
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests
from urllib.parse import urljoin

# Configuration - MUST MATCH /home/avalonas/.hermes/api/.env
USE_DB_AUTHENTICATION = os.environ.get("USE_DB_AUTHENTICATION", "false").lower() == "true"
FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY", "") if not USE_DB_AUTHENTICATION else ""

# Core symbols to track (from gematria_database.json)
CORE_SYMBOLS = {124, 666, 963, 55, 111, 279}  # Primary core symbols
EXTENDED_SYMBOLS = {285, 6966, 777, 15131, 764}  # Extended symbolic system

# Service endpoints
LOCAL_FIRECRAWL_URL = "http://localhost:3002/v1/search"
CLOUD_FIRECRAWL_URL = "https://api.firecrawl.dev/v1"
SEARXNG_URL = "http://localhost:8084/search"


class Composer:
    """Orchestrator for overnight research creating Tolaria structured notes."""

    def __init__(self):
        self.session = requests.Session()
        self.local_api_base_url = LOCAL_FIRECRAWL_URL
        self.cloud_api_base_url = CLOUD_FIRECRAWL_URL
        self.searxng_base_url = SEARXNG_URL
        
        # Output directories for Tolaria structured notes
        self.working_dir = Path("/home/avalonas/.hermes/gematria/unified_overnight_research")
        self.symbols_dir = self.working_dir / "symbols"
        self.forces_dir = self.working_dir / "forces"
        self.domain_dir = self.working_dir / "domain"
        self.research_dir = self.working_dir / "research"
        self.logs_dir = self.working_dir / "logs"
        
        # Ensure directories exist
        for d in [self.symbols_dir, self.forces_dir, self.domain_dir, self.research_dir, self.logs_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def log(self, message: str, level: str = "INFO") -> None:
        """Log message with timestamp to console and logs directory."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
        # Also write to log file
        log_file = self.logs_dir / f"overnight_{datetime.now().strftime('%Y-%m-%d')}.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")

    def check_service_health(self, url: str) -> Dict[str, Any]:
        """Check if a service is healthy and return detailed status."""
        try:
            if "/health" in url:
                response = self.session.get(url, timeout=5)
                return {
                    "healthy": response.status_code == 200 or "healthy" in response.text.lower(),
                    "status_code": response.status_code,
                    "url": url
                }
            
            # For /v1/search endpoints, test with a simple query
            test_data = {"query": "test"}
            if url.startswith("http://localhost") or url.startswith("http://127.0.0.1"):
                response = self.session.post(url, json=test_data, timeout=10)
                return {
                    "healthy": response.status_code in [200, 401],
                    "status_code": response.status_code,
                    "url": url,
                    "type": "local_firecrawl" if "localhost:3002" in url else None
                }
            else:
                # Cloud or SearXNG
                if "/search" in url and "format=json" not in url:
                    params = {"q": "test", "format": "json"}
                    response = self.session.get(url, params=params, timeout=10)
                else:
                    data = {"query": "test"}
                    response = self.session.post(url, json=data, timeout=10)
                
                return {
                    "healthy": response.status_code == 200,
                    "status_code": response.status_code,
                    "url": url,
                    "type": "searxng" if "8084" in url else "cloud_firecrawl"
                }
                
        except Exception as e:
            self.log(f"Health check failed for {url}: {e}", "WARNING")
            return {
                "healthy": False,
                "status_code": 0,
                "error": str(e),
                "url": url
            }

    def search_firecrawl_local(self, query: str) -> Dict[str, Any]:
        """Search using local Firecrawl v1.9.0 API."""
        # v1.9.0 format: simple {"query": "..."} (no options parameter)
        payload = {"query": query}
        
        self.log(f"Searching local Firecrawl: {query[:80]}...", "INFO")
        
        try:
            response = self.session.post(
                self.local_api_base_url, 
                json=payload, 
                timeout=120
            )
            
            if response.status_code == 200:
                results = response.json()
                # Handle both list (search results) and dict (scrape) responses
                data = results.get('data', {})
                if isinstance(data, list):
                    self.log(f"Local Firecrawl returned {len(data)} search results", "INFO")
                elif isinstance(data, dict) and 'scrapeResultsCount' in data:
                    self.log(f"Local Firecrawl returned {data['scrapeResultsCount']} pages", "INFO")
                else:
                    self.log(f"Local Firecrawl returned results", "INFO")
                return results
                
            elif response.status_code == 401:
                # Auth required - may need cloud fallback
                self.log("Local Firecrawl requires authentication, trying cloud...", "WARNING")
                return self.search_firecrawl_cloud(query)
            
            else:
                self.log(f"Local Firecrawl error {response.status_code}: {response.text[:200]}", "ERROR")
                # Fallback to SearXNG
                self.log("Falling back to SearXNG-Clean", "INFO")
                return self.search_searxng(query)
                
        except Exception as e:
            self.log(f"Local Firecrawl error: {e}", "ERROR")
            return {"error": str(e)}

    def search_firecrawl_cloud(self, query: str) -> Dict[str, Any]:
        """Search using cloud Firecrawl API."""
        if not FIRECRAWL_API_KEY:
            self.log("No FIRECRAWL_API_KEY configured, skipping cloud", "WARNING")
            return {"error": "No API key"}
        
        payload = {
            "query": query,
            "options": {
                "mode": "fast"  # Simple scrape mode
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}"
        }
        
        self.log("Searching cloud Firecrawl...", "INFO")
        
        try:
            response = self.session.post(
                f"{self.cloud_api_base_url}/search",
                json=payload,
                headers=headers,
                timeout=120
            )
            
            if response.status_code == 200:
                results = response.json()
                return results
                
            else:
                self.log(f"Cloud Firecrawl error {response.status_code}", "ERROR")
                # Final fallback to SearXNG
                return self.search_searxng(query)
                
        except Exception as e:
            self.log(f"Cloud Firecrawl error: {e}", "ERROR")
            return {"error": str(e)}

    def search_searxng(self, query: str) -> Dict[str, Any]:
        """Search using SearXNG-Clean."""
        params = {
            "q": query,
            "format": "json"
        }
        
        self.log(f"Searching SearXNG-Clean: {query[:80]}...", "INFO")
        
        try:
            response = self.session.get(
                self.searxng_base_url + "/search",
                params=params,
                timeout=60
            )
            
            if response.status_code == 200:
                results = response.json()
                self.log(f"SearXNG returned {len(results.get('results', []))} results", "INFO")
                return results
                
            else:
                self.log(f"SearXNG error {response.status_code}: {response.text[:200]}", "ERROR")
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            self.log(f"SearXNG error: {e}", "ERROR")
            return {"error": str(e)}

    def extract_core_symbols(self, content: str) -> List[Dict]:
        """Extract core symbol references from web content."""
        found = []
        
        all_symbols = CORE_SYMBOLS | EXTENDED_SYMBOLS
        
        for symbol in all_symbols:
            # Look for direct mentions
            pattern = f"[{symbol}]" if isinstance(symbol, int) else f"{symbol}"
            if pattern in content or str(symbol) in content:
                # Extract context window
                idx = content.find(str(symbol))
                if idx >= 0:
                    start = max(0, idx - 100)
                    end = min(len(content), idx + 150)
                    found.append({
                        "symbol": symbol,
                        "context": content[start:end],
                        "match": str(symbol)
                    })
        
        return found

    def create_core_symbol_note(self, symbol: int, data: Dict, research_context: str) -> str:
        """Create structured Tolaria note for core symbol."""
        # Get or calculate confidence score based on occurrence count
        occurrence_count = len(data.get('mentions', []))
        if occurrence_count > 0:
            confidence_score = min(0.95, 0.60 + (occurrence_count * 0.1))
        else:
            confidence_score = 0.85
        
        # Create YAML frontmatter using unified template schema
        symbol_type = "core-symbol" if symbol in CORE_SYMBOLS else "cross-reference"
        
        wikilinks = []
        for other_sym in list(CORE_SYMBOLS)[:3]:  # Link to first 3 related symbols
            if other_sym != symbol:
                wikilinks.append(f'[[CORE_SYMBOL_{other_sym}]]')
        
        # Add elemental force links if relevant
        if "fire" in research_context.lower():
            wikilinks.append('[[ELEMENTAL_FORCE_FIRE]]')
        
        yaml_frontmatter = f'''---
type: {symbol_type}
symbol_id: {symbol}
aliases: [universal bridge, threshold, completion]
name: Core Symbol [[{symbol}]]
domains:
  - general_gematria
elemental_force: fire
confidence_score: {confidence_score:.2f}
occurrences: {occurrence_count}
created: "{datetime.now().strftime('%Y-%m-%d')}"
last_modified: "{datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}"
tags: [core, symbolic, gematria]
wikilinks:
  {chr(10).join(f'  - "{wl}"' for wl in wikilinks)}
---'''

        # Generate note content from research data
        content = f"""## [[{symbol}]] Core Symbol Analysis

**Research Context:** {research_context[:200]}...

### Occurrence Patterns:

| Source | Mention Count | Confidence | Research Timestamp |
|--------|--------------|------------|-------------------|
| Search Results | {occurrence_count} | {confidence_score:.2f} | {datetime.now().strftime('%Y-%m-%d')} |

### Analysis Summary:

Based on research findings, symbol **[{symbol}]** appears in the following patterns:

{chr(10).join(f"**Pattern:** {item['context'][:150]}..." for item in data.get('mentions', [])[:3])}

---

## Relationship Matrix:

- **[[CORE_SYMBOL_{list(CORE_SYMBOLS)[:1][0]]}]** — Complementary symbolism
- **[[ELEMENTAL_FORCE_FIRE]]** — Elemental force correlations
"""
        
        return yaml_frontmatter + content

    def create_elemental_force_note(self, force_name: str) -> str:
        """Create structured Tolaria note for elemental force."""
        force_map = {
            "fire": {"name": "🔥 Fire Force", "description": "Rapid transformation, burning, purification", 
                     "characteristics": ["instantaneous", "chain-reaction", "disruptive", "illuminating"],
                     "correlates_to": [124, 777], "complements": ["lightning", "oxygen"]},
            "earth": {"name": "🌍 Earth Force (Grounded Reality)", "description": "Foundation, stability, grounding",
                      "characteristics": ["foundational", "stabilizing", "permanent"],
                      "correlates_to": [124], "complements": ["fire"]},
            "water": {"name": "💧 Water Force (Flow/Connection)", "description": "Flow, connection, adaptation",
                      "characteristics": ["adaptive", "connecting", "fluid"],
                      "correlates_to": [124], "complements": ["air"]},
            "air": {"name": "💨 Air Force (Movement/Change)", "description": "Movement, change, circulation",
                    "characteristics": ["circulating", "changing", "moving"],
                    "correlates_to": [124], "complements": ["fire"]},
            "lightning": {"name": "⚡ Lightning Force", "description": "Rapid discharge, sudden strikes, illumination",
                         "characteristics": ["instantaneous", "chain-reaction", "disruptive", "illuminating"],
                         "correlates_to": [124], "complements": ["fire"]}
        }
        
        force_data = force_map.get(force_name.lower(), {})
        if not force_data:
            return ""
        
        # Create YAML frontmatter using elemental force template schema
        wikilinks = [f'[[CORE_SYMBOL_{sym}]]) for sym in [124, 777] if sym != 963}'
        
        yaml_frontmatter = f'''---
type: elemental-force
force_name: {force_name.lower()}
name: {force_data["name"]}
description: "{force_data["description"]}"
characteristics:
{chr(10).join(f'  - {c}' for c in force_data["characteristics"])}
correlates_to:
  {chr(10).join(f'  - {s}' for s in force_data["correlates_to"])}
complements:
  {chr(10).join(f'  - {c}' for c in force_data["complements"])}
created: "{datetime.now().strftime('%Y-%m-%d')}"
tags: [elemental, {force_name.lower()}, transformation]
wikilinks:
  - "[[[CORE_SYMBOL_124]]]"
  - "[[CORE_SYMBOL_{force_data["correlates_to"][0]]}]"
---'''

        content = f"""## {force_data["name"]} — Elemental Force Matrix

The **{force_data["name"][:30]}** represents {force_data["description"]}.

### Characteristics:
{chr(10).join(f"- {c}" for c in force_data["characteristics"])}

### Correlations:
- **[[CORE_SYMBOL_124]]**: Elemental manifestations of universal bridge appear in {force_name} contexts
- **[[CORE_SYMBOL_{force_data['correlates_to'][0]}]]**: {force_data['correlates_to'][0]} symbolism complements {force_name}

---

## Relationship Matrix Entry:

| Force | Primary Symbols | Correlation Strength | Reduction Pathway |
|-------|----------------|---------------------|-------------------|
| {force_data["name"]} | {force_data["correlates_to"][:2]} | Strong | → {list(range(1, 10))} (transformation) |

"""
        
        return yaml_frontmatter + content

    def create_domain_note(self, domain_name: str, core_symbols_found: List[int], elemental_forces: List[str]) -> str:
        """Create structured Tolaria note for domain analysis."""
        # Map domain names to standardized format
        domain_map = {
            "political": {"name": "Political Domain", "core_symbol_ids": [124, 666]},
            "military": {"name": "Military Domain", "core_symbol_ids": [124, 963]},
            "religious": {"name": "Religious Domain", "core_symbol_ids": [15131, 764]},
            "geographic": {"name": "Geographic Domain", "core_symbol_ids": [124]},
            "biblical": {"name": "Biblical Domain", "core_symbol_ids": [15131, 764]},
            "historical": {"name": "Historical Domain", "core_symbol_ids": [6966]}
        }
        
        domain_data = domain_map.get(domain_name.lower(), {
            "name": f"{domain_name.title()} Domain",
            "core_symbol_ids": core_symbols_found[:3] if core_symbols_found else [124]
        })
        
        # Calculate confidence based on symbol count
        confidence_score = min(0.95, 0.75 + (len(core_symbols_found) * 0.08))
        domain_name_lower = domain_name.lower()
        pattern_frequency = "high" if len(core_symbols_found) >= 2 else "medium" if core_symbols_found else "low"
        
        # Create YAML frontmatter using domain analysis template schema
        wikilinks = [f'[[CORE_SYMBOL_{sym}]]) for sym in domain_data["core_symbol_ids"][:2]']
        
        yaml_frontmatter = f'''---
type: domain-analysis
domain_name: {domain_name.lower()}
name: {domain_data["name"]}
core_symbols:
  {chr(10).join(f'  - {sym}' for sym in domain_data["core_symbol_ids"])}
elemental_forces:
  {chr(10).join(f'  - {force}' for force in elemental_forces)}
confidence_score: {confidence_score:.2f}
created: "{datetime.now().strftime('%Y-%m-%d')}"
last_modified: "{datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}"
pattern_frequency: {pattern_frequency}
primary_elemental: {"fire" if elemental_forces else "null"}
tags: [domain, {domain_name.lower()}, analysis]
wikilinks:
{chr(10).join(f'  - "[[[CORE_SYMBOL_{sym}]])" for sym in domain_data["core_symbol_ids"][:2]}'''

        content = f"""## 🏛️ {domain_data["name"]} — Analysis Log

### Core Symbol Patterns:

The **{domain_data["name"][:40]}** shows convergence with core symbols **{', '.join(map(str, domain_data["core_symbol_ids"]))}**.

### Symbol Frequency in Domain:

| Core Symbol | Occurrence Pattern | Confidence | Domain Relevance |
|-------------|-------------------|------------|------------------|
| [[124]] | Universal bridge threshold | 0.95 | High - Appears across all subdomains |
{chr(10).join(f'| [[{sym}]] | Emerging pattern | {confidence_score:.2f} | Medium' for sym in domain_data["core_symbol_ids"][1:3])}

### Elemental Force Correlations:

**Primary Force:** {elemental_forces[0] if elemental_forces else "N/A"}  
**Secondary Forces:** {', '.join(elemental_forces[1:]) if len(elemental_forces) > 1 else "None identified"}

---

## Domain Frequency Matrix Entry:

| Domain | Primary Symbols | Elemental Force | Confidence | Pattern Density |
|--------|----------------|------------------|------------|-----------------|
| {domain_data["name"]} | {', '.join(map(str, domain_data["core_symbol_ids"]))} | {"🔥 Fire" if elemental_forces else "⏸️ Pending"} | {confidence_score:.2f} | █ High (if pattern_frequency == "high") else ▓ Medium'

"""
        
        return yaml_frontmatter + content

    def create_research_cycle_note(self, cycle_id: int, symbols_detected: List[int], domains_found: List[str]) -> str:
        """Create structured Tolaria note for research timeline entry."""
        
        # Calculate status based on results
        status = "expanded" if len(symbols_detected) >= 3 else "baseline" if symbols_detected else "ongoing"
        
        # Create YAML frontmatter using research timeline template schema
        yaml_frontmatter = f'''---
type: research-timeline
cycle_id: {cycle_id}
timestamp: "{datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}"
symbols_detected:
  {chr(10).join(f'  - {sym}' for sym in symbols_detected)}
domains_found:
  {chr(10).join(f'  - "{dom}"' for dom in domains_found)}
status: {status}
description: Cycle {cycle_id}: pattern analysis ({len(symbols_detected)} symbols detected)
created: "{datetime.now().strftime('%Y-%m-%d')}"
tags: [research, timeline, cycle-{cycle_id}]
wikilinks:
  - "[[[RESEARCH_CYCLE_{cycle_id}]]]"
---'''

        content = f"""## 📅 Research Timeline — Cycle {cycle_id}

**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Symbols Detected:** {', '.join(map(str, symbols_detected))}  
**Domains Found:** {', '.join(domains_found) if domains_found else 'None yet'}  
**Status:** {status.capitalize()}

### Cycle Tracking Log:

| Metric | Value |
|--------|-------|
| Cycle ID | auto_{cycle_id} |
| Symbol Count | {len(symbols_detected)} |
| Domains Discovered | {len(domains_found)} |
| Confidence Score | {min(0.95, 0.80 + (cycle_id * 0.02)):.2f} |

---

## Research Progression:

This is cycle **{cycle_id}** in the automated overnight research protocol. Each cycle builds upon previous findings.

### Next Steps for Cycle {cycle_id}:
1. Update CROSS_REFERENCE_INDEX.md with new symbol-domain connections
2. Check ASCII correlation heatmap for emerging patterns
3. Flag any symbols appearing across multiple domains for deeper analysis

---

## Relationship Matrix Updates:

- [[CROSS_REF_SYMBOL_DOMAIN]] — Track symbol appearances per domain
- [[CROSS_REF_ELEMENTAL_CORRELATION]] — Elemental force convergence patterns
"""
        
        return yaml_frontmatter + content

    def create_cross_reference_note(self, pattern_id: str, symbol_ids: List[int], domains_affected: List[str], 
                                    synthesis_notes: str) -> str:
        """Create structured Tolaria note for cross-reference relationships."""
        
        # Create YAML frontmatter using cross-reference template schema
        confidence_score = 0.78 if len(symbol_ids) >= 3 else 0.65
        
        wikilinks = [f'[[CORE_SYMBOL_{sym}]]) for sym in symbol_ids[:3]']
        wikilinks.append('[[ELEMENTAL_FORCE_FIRE]]')
        
        yaml_frontmatter = f'''---
type: cross-reference
pattern_id: {pattern_id}
symbol_ids:
  {chr(10).join(f'  - {sym}' for sym in symbol_ids)}
confidence_score: {confidence_score:.2f}
domains_affected:
{chr(10).join(f'  - "{dom}"' for dom in domains_affected)}
synthesis_notes: "{synthesis_notes[:500]}"
created: "{datetime.now().strftime('%Y-%m-%d')}"
tags: [cross-reference, pattern-{pattern_id}]
wikilinks:
{chr(10).join(f'  - "[[{wl}]]" for wl in wikilinks)}
---'''

        content = f"""## 🔗 Pattern Cross-Reference Index: {pattern_id}

**Relevance Score:** {confidence_score:.2f}  
**Domains Affected:** {', '.join(domains_affected) if domains_affected else 'Universal (all domains)'}  
**Core Symbols Involved:** {', '.join(map(str, symbol_ids))}

### Relationship Tracking:

- **[[CORE_SYMBOL_{symbol_ids[0]]}]** — Primary relationship anchor
- **[[ELEMENTAL_FORCE_FIRE]]** — Elemental force correlation

---

## Cross-Reference Pattern Documentation:

This entry documents the symbolic convergence pattern **{pattern_id[:30]}...**.

### Symbolic Connection:
""" + synthesis_notes.replace("\n", "\n\n") + """"

        return yaml_frontmatter + content

    def save_note(self, note_type: str, note_content: str) -> Path:
        """Save a structured Tolaria note to the appropriate directory."""
        # Create filename from first 50 chars of note content
        hash_id = hash(note_content[:20]) % 10000  # Simple hash for ID
        
        if note_type == "core-symbol":
            output_dir = self.symbols_dir
            filename = f"CORE_SYMBOL_{hash_id:04d}.md"
        elif note_type == "elemental-force":
            output_dir = self.forces_dir
            filename = f"ELEMENTAL_FORCE_{hash_id:04d}.md"
        elif note_type == "domain-analysis":
            output_dir = self.domain_dir
            filename = f"DOMAIN_{note_content.split('name:', 1)[1].split('\n')[0].strip()[:50]}".replace(" ", "_").replace("/", "") + ".md" if len(note_content.split('name:', 1)) > 1 else f"DOMAIN_{hash_id:04d}.md"
        elif note_type == "cross-reference":
            output_dir = self.working_dir / "cross_reference"
            filename = f"CROSS_REF_{hash_id:04d}.md"
        elif note_type == "research-timeline":
            output_dir = self.research_dir
            filename = f"RESEARCH_CYCLE_{hash_id:04d}.md"
        
        # Ensure directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = output_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(note_content)
        
        self.log(f"Saved Tolaria note to {filepath.name}", "INFO")
        return filepath

    def generate_oversight_report(self, search_results: Dict[str, Any], query: str) -> str:
        """Generate oversight report from search results."""
        # Check all available sources
        health_status = self.check_service_health(SEARXNG_URL)
        
        report_lines = [
            "=" * 70,
            "GEMATRIA OVERSIGHT REPORT (TOLARIA EDITION)",
            f"Query: {query[:100]}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 70,
            "",
            "SERVICE HEALTH:",
        ]
        
        # Include search results summary
        data = search_results.get("data", {})
        if "scrapeResultsCount" in data:
            report_lines.append(f"\nLOCAL FIRECRAWL RESULTS: {data['scrapeResultsCount']} pages found")
        elif "results" in search_results:
            report_lines.append(f"\nSEARXNG RESULTS: {len(search_results.get('results', []))} results found")
        
        # Core symbols found
        extracted = self.extract_core_symbols(str(search_results))
        if extracted:
            symbol_mentions = [str(x['symbol']) for x in extracted]
            report_lines.append(f"\nCORE SYMBOLS MENTIONED IN RESULTS:")
            for sym in symbol_mentions:
                report_lines.append(f"  • {sym}")
        
        report_lines.extend([
            "",
            "=" * 70,
            "TOLARIA STRUCTURED NOTES GENERATED:",
            "1. Core Symbol notes ([[CORE_SYMBOL_XXXX]])",
            "2. Elemental Force notes ([[ELEMENTAL_FORCE_XXX]])",
            "3. Domain Analysis notes ([[DOMAIN_XXX]])",
            "4. Cross-Reference notes (CROSS_REF_ID)",
            "=" * 70,
        ])
        
        return "\n".join(report_lines)

    def run_full_analysis(self, query: str = None) -> bool:
        """Run full overnight research analysis creating Tolaria structured notes."""
        if query is None:
            query = "gematria patterns core symbols 124 963 55 111"
        
        print("=" * 70)
        print("STEVE'S GEMATRIA COMPOSER - OVERNIGHT RESEARCH (TOLARIA EDITION)")
        print("=" * 70)
        print(f"\nSearch Query: {query}")
        print(f"\nTarget Directory: {self.working_dir.absolute()}")
        print()

        # Search
        results = self.search_firecrawl_local(query)
        
        # Generate oversight report
        if "error" in results:
            self.log(f"Error: {results['error']}", "ERROR")
            return False
        
        report = self.generate_oversight_report(results, query)
        print(report)
        
        # Create core symbol notes from search results
        extracted = self.extract_core_symbols(str(results))
        for mention in extracted[:5]:  # Create up to 5 core symbol notes
            note_type = "core-symbol" if mention['symbol'] in CORE_SYMBOLS else "cross-reference"
            note_content = self.create_core_symbol_note(mention['symbol'], 
                                                         {"mentions": [mention]},
                                                         query)
            filepath = self.save_note(note_type, note_content)
        
        print("\n✅ Overnight research complete!")
        print(f"   Tolaria structured notes saved to: {self.working_dir.absolute()}")
        print("   Check /logs/overnight_YYYY-MM-DD.log for details\n")
        
        return True


def main():
    """Main entry point for Composer."""
    
    # Initialize composer
    composer = Composer()
    
    # Parse command line args (for manual testing)
    query = sys.argv[1] if len(sys.argv) > 1 else "gematria patterns core symbols"
    
    # Run overnight research
    success = composer.run_full_analysis(query)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
