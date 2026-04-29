#!/usr/bin/env python3
"""
Tolaria Overnight Research Push Script

This script reads research results from the unified_overnight_research 
reports directory and pushes formatted summaries to the Tolaria Discord channel.

Usage:
    python push_to_tolaria.py
    # or via cron job
"""

import os
import json
import datetime
import glob

# Configuration
REPORTS_DIR = "/home/avalonas/.hermes/gematria/unified_overnight_research/reports"
WEBHOOK_URL = "https://discordapp.com/api/webhooks/1498991426393083988/MA4A6cQLp2zZZiPDQnW_hIlqqf7zOMgi1pX5mbOWJabdowqWVhJ3OAoDfdIZ0oGB0TJm"
WEBHOOK_CHANNEL = "#tolaria-choose-your-own-poison"

# Gematria alphabetic values for encoding
GEMATRIA_VALUES = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10,
    'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9, 'S': 1,
    'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8
}

def read_file(filepath):
    """Read a markdown file and return its content."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""

def extract_key_sections(markdown_content):
    """Extract key sections from markdown for summary."""
    sections = {
        'overview': '',
        'patterns': [],
        'coordinates': [],
        'next_steps': []
    }
    
    current_section = 'overview'
    
    for line in markdown_content.split('\n'):
        if line.startswith('# ') and '#' not in line[2:]:  # Top-level section
            current_section = line[2:].strip()
            continue
            
        if '## Pattern Hypotheses' in line or '### Pattern H' in line:
            current_section = 'patterns'
        elif '## Geographic Coordinates' in line:
            current_section = 'coordinates'
        elif '## Next Steps' in line or 'Next Steps' in line:
            current_section = 'next_steps'
            
        sections[current_section].append(line)
        
    return sections

def encode_gematria(text):
    """Apply gematria reduction to text for symbolic encoding."""
    result = ""
    for char in text:
        if char.upper() in GEMATRIA_VALUES:
            result += str(GEMATRIA_VALUES[char.upper()])
        else:
            result += char
    return result

def generate_thermal_map(intensities):
    """Generate ASCII thermal map based on intensity values."""
    scale = "░ ▒ ▓ █"
    max_val = max(intensities) if intensities else 1
    
    lines = []
    for val in intensities:
        ratio = val / max_val if max_val > 0 else 0
        lines.append(scale[int(ratio * len(scale)) + 0])
    
    return "\n".join(lines)

def format_file_summary(filepath, content):
    """Generate a formatted summary for a single file."""
    filename = os.path.basename(filepath)
    
    # Extract frontmatter tags if present
    frontmatter_tags = []
    if '---' in content[:100]:  # Check first 100 chars
        try:
            end_idx = content.index('---', 4)
            yaml_content = content[4:end_idx]
            for line in yaml_content.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    if 'tags' in key:
                        tags = [t.strip().strip('"').strip("'") 
                               for t in value.split(',') if t.strip()]
                        frontmatter_tags.extend(tags)
        except:
            pass
    
    sections = extract_key_sections(content)
    
    # Generate summary text
    summary_lines = []
    
    # Title with ASCII decoration
    title_length = len(filename) + 6
    summary_lines.append("=" * title_length)
    summary_lines.append(f"  {filename.upper()}")
    summary_lines.append("=" * title_length)
    summary_lines.append("")
    
    # Frontmatter tags
    if frontmatter_tags:
        summary_lines.append(f"# Tags: {', '.join(frontmatter_tags)}")
        summary_lines.append("")
    
    # Overview section (first paragraph)
    overview_text = '\n'.join(sections['overview'][:5])  # First 5 lines
    for line in overview_text.split('\n'):
        if line.strip():
            summary_lines.append(f"> {line.strip()}")
    summary_lines.append("")
    
    # Pattern sections
    for pattern_type, pattern_lines in [('Patterns', sections['patterns']), 
                                        ('Coordinates', sections['coordinates'])]:
        if pattern_lines:
            summary_lines.append(f"### {pattern_type} Highlights:")
            for line in pattern_lines[:3]:  # Top 3 lines per section
                if line.strip():
                    summary_lines.append(f"    - {line.strip()}")
            summary_lines.append("")
    
    # Next steps
    next_steps_text = '\n'.join(sections['next_steps'][:4])
    for line in next_steps_text.split('\n'):
        if '[ ]' in line or line.strip():
            summary_lines.append(f"* {line.strip()}")
    summary_lines.append("")
    
    return "\n".join(summary_lines)

def main():
    """Main function to generate and push research summaries."""
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Starting Tolaria research push...")
    
    # Find all markdown files in reports directory
    report_files = glob.glob(os.path.join(REPORTS_DIR, "**/*.md"), recursive=True)
    
    if not report_files:
        print("No report files found. Exiting.")
        return
    
    print(f"Found {len(report_files)} report files to process.")
    
    # Generate summaries for all reports
    all_summaries = []
    file_summaries = {}
    
    for filepath in sorted(report_files):
        try:
            content = read_file(filepath)
            if content.strip():  # Only process non-empty files
                summary = format_file_summary(filepath, content)
                file_summaries[filepath] = {
                    'summary': summary,
                    'timestamp': datetime.datetime.now().isoformat()
                }
                all_summaries.append(f">>> {os.path.basename(filepath)}\n{summary}\n---")
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
    
    # Build final message structure
    header = """📊 STEVE'S GEMATRIA OVERNIGHT RESEARCH PUSH 📊

# Analysis Cycle: $(date +%Y-%m-%d) UTC

## Reports Processed:
"""
    
    for filepath, data in file_summaries.items():
        header += f"\n- `{os.path.basename(filepath)}` ({data['timestamp']})\n"
    
    footer = """

---
# Legend: ░ Low | ▒ Medium-Low | ▓ Medium-High | █ High | . Void | O Neutral

*Analysis generated by unified_overnight_research pipeline.*
"""
    
    full_message = header + "\n".join(all_summaries) + footer
    
    # Log to console
    print("\n" + "=" * 60)
    print("PREVIEW OF MESSAGE TO TOLARIA:")
    print("=" * 60)
    print(full_message[:3000])  # Preview first 3000 chars
    print("... (truncated for console display)")
    print("=" * 60)
    
    # For actual posting, would use requests library or curl:
    import requests
    try:
        response = requests.post(WEBHOOK_URL, data={'content': full_message}, timeout=30)
        print(f"[+] Posted to Tolaria! Status: {response.status_code}")
        if response.status_code == 204:
            print("[✓] Message successfully delivered to #tolaria-choose-your-own-poison")
        else:
            print(f"[!] Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"[-] Failed to post to webhook: {e}")
    
    print("\n[+] Message generation complete.")
    print("    To actually post to Discord, uncomment the requests.post() call above")
    print(f"[+] Output saved to console. Ready for webhook delivery.\n")
    
    return file_summaries

if __name__ == "__main__":
    main()
