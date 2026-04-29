#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STEVE'S GEMATRIA - ASCII CORRELATION HEATMAP GENERATOR
Generates real-time ASCII/HTML visualizations for Tolaria vault

Heat scale encoding (consistent across all visualizations):
  █ = Strongest (0.95+) — Core symbol convergence
  ▓ = High (0.85-0.94) — Frequent cross-domain appearance  
  ▒ = Medium-High (0.70-0.84) — Occasional manifestations
  ░ = Weak-Medium (0.60-0.69) — Needs investigation
  . = Low (<0.59) — Rare occurrences
  o = Very weak
  ^ = Null/No data

Outputs:
1. ASCII art heatmap for terminal display
2. HTML matrix for Obsidian/Tolaria web vault
3. Terminal animations with heat scale encoding
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import json

# Color palette for ASCII output
HEAT_SCALE_ENCODING = {
    "█": 0.95,      # Strongest - Core symbol convergence
    "▓": 0.875,     # High - Frequent cross-domain appearance
    "▒": 0.8,       # Medium-High - Occasional manifestations
    "░": 0.7,       # Weak-Medium - Needs investigation
    ".": 0.55,      # Low - Rare occurrences
    "o": 0.3,       # Very weak
    "^": 0.0,       # Null/No data
    " ": -1,        # Empty/null
}

REVERSE_HEAT_SCALE = {v: k for k, v in HEAT_SCALE_ENCODING.items()}


class HeatmapGenerator:
    """ASCII/HTML correlation heatmap generator for Tolaria vault."""

    def __init__(self, working_dir: str = "/home/avalonas/.hermes/gematria/unified_overnight_research"):
        self.working_dir = Path(working_dir)
        self.symbols_dir = self.working_dir / "symbols"
        self.forces_dir = self.working_dir / "forces"
        self.domain_dir = self.working_dir / "domain"
        
        # Load core symbol data from Tolaria notes
        self.core_symbols: Dict[int, Dict] = {}
        self.elemental_forces: Dict[str, Dict] = {}
        self.domains: Dict[str, Dict] = {}
        
        # Load existing Tolaria notes
        self._load_tolaria_notes()

    def _load_tolaria_notes(self) -> None:
        """Load structured Tolaria notes from YAML frontmatter."""
        
        def parse_yaml_frontmatter(filepath: Path) -> Optional[Dict]:
            """Parse YAML frontmatter from a .md file."""
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                frontmatter_end = 0
                
                # Find end of frontmatter (---)
                for i, line in enumerate(lines):
                    if line.strip() == '---':
                        frontmatter_end = i + 1
                        break
                
                if frontmatter_end == 0:
                    return None
                
                frontmatter_text = '\n'.join(lines[:frontmatter_end])
                
                # Simple YAML parsing
                data = {}
                for line in frontmatter_text.split('\n'):
                    if ':' in line and not line.strip().startswith('#'):
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Parse arrays (multiline YAML)
                        if value == '':
                            continue
                        
                        # Parse numeric values
                        try:
                            if '.' in value:
                                data[key] = float(value)
                            else:
                                data[key] = int(value)
                        except ValueError:
                            data[key] = value
                
                return data
            except Exception as e:
                print(f"Warning: Could not parse {filepath}: {e}")
                return None
        
        # Load core symbol notes
        for filepath in self.symbols_dir.glob("CORE_SYMBOL_*.md"):
            data = parse_yaml_frontmatter(filepath)
            if data and 'symbol_id' in data:
                symbol_id = data['symbol_id']
                self.core_symbols[symbol_id] = data
        
        # Load elemental force notes
        for filepath in self.forces_dir.glob("ELEMENTAL_FORCE_*.md"):
            data = parse_yaml_frontmatter(filepath)
            if data and 'force_name' in data:
                force_name = data['force_name']
                self.elemental_forces[force_name] = data
        
        # Load domain analysis notes
        for filepath in self.domain_dir.glob("DOMAIN_*.md"):
            data = parse_yaml_frontmatter(filepath)
            if data and 'domain_name' in data:
                domain_name = data['domain_name']
                self.domains[domain_name] = data

    def generate_symbol_correlation_matrix(self) -> str:
        """Generate ASCII correlation matrix between core symbols."""
        
        if not self.core_symbols:
            return "⚠️ No core symbol notes found. Run overnight research first."
        
        # Sort symbols by ID for consistent ordering
        sorted_symbols = sorted(self.core_symbols.keys())
        
        # Build correlation data (simplified - use confidence scores as proxies)
        rows = []
        
        # Header row
        header = "  " + " ".join(f"{sid:4}" for sid in sorted_symbols[:10])
        rows.append(header)
        
        # Separator
        sep = "  +" + "+" * len(sorted_symbols[:10])
        rows.append(sep)
        
        # Data rows
        for row_sym_id in sorted_symbols[:10]:
            row_data = self.core_symbols[row_sym_id]
            confidence = getattr(row_data, 'confidence_score', 0.85) if isinstance(row_data, dict) else 0.85
            
            # Simplified correlation: use shared domains as proxy
            row_cells = []
            for col_sym_id in sorted_symbols[:10]:
                col_data = self.core_symbols.get(col_sym_id)
                if col_data:
                    shared_domains = set(row_data.get('domains', [])).intersection(set(col_data.get('domains', [])))
                    correlation_strength = len(shared_domains) / max(len(row_data.get('domains', [])), 1) * confidence
                else:
                    correlation_strength = 0
                
                # Convert to ASCII character
                cell_char = get_heat_scale_char(correlation_strength)
                row_cells.append(f" {cell_char} ")
            
            row = f"[[{row_sym_id:3}]] " + "".join(row_cells)
            rows.append(row)
        
        return "\n".join(rows)

    def generate_domain_convergence_matrix(self) -> str:
        """Generate ASCII convergence matrix showing domain-symbol overlap."""
        
        if not self.domains and not self.core_symbols:
            return "⚠️ No domain or core symbol notes found. Run overnight research first."
        
        # Get all unique symbols mentioned in domains
        all_symbols = sorted(set(self.core_symbols.keys()) | 
                            {int(s) for s in str(self.domains).split() if any(x.isdigit() for x in s.split('['))})[:15]
        
        # Build matrix header
        lines = []
        lines.append("Domain Convergence Matrix — Symbol Appearance Density")
        lines.append("=" * 70)
        lines.append("")
        
        # Get domains sorted by confidence
        domain_rows = [(name, data) for name, data in self.domains.items()]
        domain_rows.sort(key=lambda x: getattr(x[1], 'confidence_score', 0.85), reverse=True)
        
        # Column headers (symbols)
        header = "Domain" + " │ ".join(f"{sid:5}" for sid in all_symbols[:6])
        lines.append(header)
        lines.append("-" * len(header))
        
        # Data rows
        for domain_name, domain_data in domain_rows[:8]:  # Limit to top 8 domains
            confidence = getattr(domain_data, 'confidence_score', 0.75) if isinstance(domain_data, dict) else 0.75
            
            row_cells = []
            for sym_id in all_symbols[:6]:
                sym_data = self.core_symbols.get(sym_id)
                domain_data_obj = domain_data if isinstance(domain_data, dict) else data
                
                # Calculate overlap: does this domain track this symbol?
                domains_list = getattr(domain_data_obj, 'domains', []) if isinstance(domain_data_obj, type(self.domains)) else []
                
                if sym_id in domains_list:
                    cell_char = get_heat_scale_char(confidence)
                elif self.core_symbols.get(sym_id):  # Symbol exists but not in this domain
                    cell_char = "░"
                else:
                    cell_char = "^"
                
                row_cells.append(cell_char)
            
            line = f"{domain_name[:12]:>14}" + " │ ".join(row_cells)
            lines.append(line)
        
        # Add confidence legend at bottom
        lines.append("")
        lines.append("Heat Scale Encoding (consistent across all visualizations):")
        lines.append(f"  █ Strongest   = 0.95+ — Core symbol convergence")
        lines.append(f"  ▓ High         = 0.85-0.94 — Frequent cross-domain appearance")
        lines.append(f"  ▒ Medium-High  = 0.70-0.84 — Occasional manifestations")
        lines.append(f"  ░ Weak-Medium  = 0.60-0.69 — Needs investigation")
        lines.append(f"  . Low          = <0.59 — Rare occurrences")
        lines.append(f"  ^ Null         = No data tracked for this domain-symbol pair")
        lines.append("")
        
        return "\n".join(lines)

    def generate_elemental_correlation_heatmap(self) -> str:
        """Generate ASCII heatmap showing elemental force correlations."""
        
        if not self.elemental_forces and not self.core_symbols:
            return "⚠️ No elemental force or core symbol notes found. Run overnight research first."
        
        lines = []
        lines.append("Elemental Force Correlation Heatmap — Symbol/Domain Overlap")
        lines.append("=" * 70)
        lines.append("")
        
        # Get forces sorted by confidence
        force_rows = [(name, data) for name, data in self.elemental_forces.items()]
        force_rows.sort(key=lambda x: getattr(x[1], 'confidence_score', 0.85), reverse=True)
        
        header = "Force" + " │ ".join(f"{sid:5}" for sid in sorted(self.core_symbols.keys())[:6])
        lines.append(header)
        lines.append("-" * len(header))
        
        # Data rows
        for force_name, force_data in force_rows[:5]:  # Top 5 forces
            confidence = getattr(force_data, 'confidence_score', 0.75) if isinstance(force_data, dict) else 0.75
            
            row_cells = []
            for sym_id in sorted(self.core_symbols.keys())[:6]:
                sym_data = self.core_symbols.get(sym_id)
                
                # Check correlation: does this force correlate with this symbol?
                correlates_to = getattr(force_data, 'correlates_to', []) if isinstance(force_data, dict) else []
                
                if sym_id in correlates_to:
                    cell_char = get_heat_scale_char(confidence + 0.15)  # Boost for direct correlation
                elif self.core_symbols.get(sym_id):
                    cell_char = "░"
                else:
                    cell_char = "^"
                
                row_cells.append(cell_char)
            
            line = f"{force_data['name'][:8]:>10}" + " │ ".join(row_cells)
            lines.append(line)
        
        # Add forces not in notes (using core symbols as proxy)
        lines.extend([])
        lines.append("")
        lines.append("Note: Forces shown are from existing Tolaria notes.")
        lines.append(f"Other forces correlate to [[124]] by default.")
        lines.append("")
        
        return "\n".join(lines)

    def generate_complete_overview(self) -> str:
        """Generate comprehensive ASCII overview with all matrices."""
        
        sections = []
        
        # Title
        sections.append("=" * 70)
        sections.append("STEVE'S GEMATRIA — TOLARIA CORRELATION OVERVIEW")
        sections.append("=" * 70)
        sections.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sections.append("")
        
        # Core symbol counts
        sections.append(f"Core Symbols Tracked:     {len(self.core_symbols)}")
        sections.append(f"Elemental Forces Tracked: {len(self.elemental_forces)}")
        sections.append(f"Domains Analyzed:         {len(self.domains)}")
        sections.append("")
        
        # Separator
        sections.append("-" * 70)
        sections.append("")
        
        # Core symbol matrix
        sym_matrix = self.generate_symbol_correlation_matrix()
        if sym_matrix.startswith("⚠️"):
            sections.append(sym_matrix)
        else:
            sections.append("Core Symbol Correlation Matrix:")
            sections.append(sym_matrix)
            sections.append("")
        
        # Domain convergence matrix
        dom_matrix = self.generate_domain_convergence_matrix()
        if dom_matrix.startswith("⚠️"):
            sections.append(dom_matrix)
        else:
            sections.append("Domain Convergence Matrix:")
            sections.append(dom_matrix)
            sections.append("")
        
        # Elemental correlation heatmap
        elem_matrix = self.generate_elemental_correlation_heatmap()
        if elem_matrix.startswith("⚠️"):
            sections.append(elem_matrix)
        else:
            sections.append("Elemental Correlation Heatmap:")
            sections.append(elem_matrix)
            sections.append("")
        
        # Symbol frequency table
        sections.append("-" * 70)
        sections.append("")
        sections.append("Symbol Frequency Table — Occurrence Count by Domain")
        sections.append("=" * 70)
        sections.append("")
        
        # Build frequency table header
        freq_header = "Symbol │" + " │ ".join(f"{d[:12]:>14}" for d in sorted(self.domains.keys(), key=lambda x: len(x))[:6])
        sections.append(freq_header)
        sections.append("-" * len(freq_header))
        
        # Frequency data rows
        for sym_id in sorted(self.core_symbols.keys())[:8]:
            sym_data = self.core_symbols[sym_id]
            
            row_cells = []
            for domain_name in sorted(self.domains.keys(), key=lambda x: len(x))[:6]:
                if domain_name in str(sym_data) if isinstance(sym_data, dict) else "":
                    # Calculate approximate occurrence count based on domains
                    occ_count = len(sym_data.get('domains', [])) * 2
                    cell_char = get_heat_scale_char(min(0.95, occ_count / 10))
                else:
                    cell_char = "^"
                
                row_cells.append(cell_char)
            
            row_line = f"[[{sym_id:3}]] │ " + "".join(row_cells)
            sections.append(row_line)
        
        sections.append("")
        sections.append("Heat Scale Encoding:")
        sections.append(f"  █ Strongest   = 0.95+ — Core symbol convergence")
        sections.append(f"  ▓ High         = 0.85-0.94 — Frequent cross-domain appearance")
        sections.append(f"  ▒ Medium-High  = 0.70-0.84 — Occasional manifestations")
        sections.append(f"  ░ Weak-Medium  = 0.60-0.69 — Needs investigation")
        sections.append(f"  . Low          = <0.59 — Rare occurrences")
        sections.append(f"  ^ Null         = No data tracked")
        sections.append("")
        sections.append("=" * 70)
        
        return "\n".join(sections)

    def generate_html_matrix(self, matrix_name: str, matrix_data: Dict[str, Any]) -> str:
        """Generate HTML representation of correlation matrix for Obsidian/Tolaria."""
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{matrix_name} — Tolaria Vault</title>
    <style>
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #0d1117;
            color: #c9d1d9;
            padding: 2rem;
            margin: 0;
        }}
        
        h1 {{
            color: #f0f6fc;
            border-bottom: 2px solid #30363d;
            padding-bottom: 0.5rem;
        }}
        
        .matrix-container {{
            margin-top: 2rem;
            overflow-x: auto;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            font-size: 13px;
        }}
        
        th, td {{
            padding: 8px 6px;
            text-align: center;
            border: 1px solid #30363d;
        }}
        
        th {{
            background: #161b22;
            color: #ff7b72;
            font-weight: 600;
        }}
        
        td {{
            background: #0d1117;
            font-family: 'Menlo', 'Monaco', monospace;
        }}
        
        .heat-█ {{ background: linear-gradient(135deg, #ff4444 0%, #aa0000 100%); color: white; font-weight: bold; }}
        .heat-▓ {{ background: linear-gradient(135deg, #ff8800 0%, #aa6600 100%); color: white; font-weight: bold; }}
        .heat-▒ {{ background: linear-gradient(135deg, #ffcc00 0%, #aa9900 100%); color: black; }}
        .heat-░ {{ background: linear-gradient(135deg, #44ff44 0%, #00aa00 100%); color: white; font-weight: bold; }}
        .heat-. {{ background: linear-gradient(135deg, #888888 0%, #555555 100%); color: #666; }}
        .heat-o {{ background: linear-gradient(135deg, #5588aa 0%, #446677 100%); color: white; }}
        .heat-^ {{ background: transparent; color: #444; font-style: italic; }}
        
        .legend {{
            margin-top: 2rem;
            padding: 1rem;
            background: #161b22;
            border-radius: 6px;
            display: flex;
            align-items: center;
            gap: 1.5rem;
            flex-wrap: wrap;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .legend-box {{
            width: 16px;
            height: 16px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <h1>{matrix_name}</h1>
    {html}
</body>
</html>
"""
        return html


def get_heat_scale_char(confidence: float) -> str:
    """Get ASCII character for confidence score."""
    if confidence >= 0.95:
        return "█"
    elif confidence >= 0.875:
        return "▓"
    elif confidence >= 0.8:
        return "▒"
    elif confidence >= 0.7:
        return "░"
    elif confidence >= 0.6:
        return "."
    elif confidence > 0:
        return "o"
    else:
        return "^"


def main():
    """Main entry point for heatmap generator."""
    
    print("=" * 70)
    print("STEVE'S GEMATRIA — TOLARIA HEATMAP GENERATOR")
    print("=" * 70)
    print()
    
    # Initialize generator
    generator = HeatmapGenerator()
    
    # Generate ASCII overview
    overview = generator.generate_complete_overview()
    print(overview)
    
    # Save to file in scripts directory
    output_file = Path("/home/avalonas/.hermes/gematria/unified_overnight_research/scripts/HEATMAP_OVERVIEW.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(overview)
    
    print(f"\n✅ ASCII heatmap saved to: {output_file.absolute()}")
    print()
    
    # Generate HTML for Tolaria/Obsidian
    html_output = generator.generate_html_matrix(
        "Tolaria Correlation Overview",
        {
            "core_symbols": len(generator.core_symbols),
            "elemental_forces": len(generator.elemental_forces),
            "domains": len(generator.domains)
        }
    )
    
    html_file = Path("/home/avalonas/.hermes/gematria/unified_overnight_research/scripts/tolaria_correlation_matrix.html")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_output)
    
    print(f"✅ HTML heatmap saved to: {html_file.absolute()}")
    print("   Open in browser or embed in Tolaria vault")
    print()
    
    return overview


if __name__ == "__main__":
    main()
