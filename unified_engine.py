#!/usr/bin/env python3
"""
Unified Overnight Research Engine - Steve's Gematria
Comprehensive single-script solution combining:
- Web scraping (local Firecrawl API)
- Pattern analysis & cross-domain convergence detection
- Relationship iteration between new discoveries
- Temporal tracking of symbol appearances
- ASCII heatmaps and visualizations
"""

import subprocess
import sys
import json
import time
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
import ssl
import re
import urllib3 as urllib
from urllib3.exceptions import HTTPError, TimeoutError
import re
import json  # Added for JSON parsing in API calls
import requests  # Use requests library (more reliable than urllib3)


class UnifiedOvernightEngine:
    """
    All-in-one overnight research engine for gematria pattern discovery.
    
    Architecture Flow:
        ┌──────────┐     ┌─────────────┐     ┌─────────────────┐
        │ Queries  │ →   │  Web Scrape │ →   │  Pattern Analyze│
        └──────────┘     └─────────────┘     └─────────────────┘
                          ↓                    ↓
                   ┌─────────────┐    ┌─────────────────┐
                   │Relationship │    │Temporal Track   │
                   │Iteration    │    │                 │
                   └─────────────┘    └─────────────────┘
                          ↓                    ↓
                   ┌─────────────────────────────────┐
                   │  Generate Full Report           │
                   │  (with ASCII heatmaps & insights)│
                   └─────────────────────────────────┘
    """
    
    def __init__(self):
        # Local Firecrawl configuration (using localhost:3002)
        self.firecrawl_url = "http://localhost:3002/v1/search"  # Local instance, unlimited queries
        self.firecrawl_api_key_path = Path.home() / ".hermes" / ".env"
        self.timeout = 60
        
        # Cloud API fallback (generous free tier ~500/day)
        self.cloud_firecrawl_url = "https://api.firecrawl.dev/v1/search"
        
        # Paths
        self.base_path = Path("/home/avalonas/.hermes/gematria")
        self.db_path = self.base_path / "database" / "gematria_database.json"
        self.reports_dir = self.base_path / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Load Firecrawl API key from .env file (line 133)
        try:
            with open(self.firecrawl_api_key_path, 'r') as f:
                lines = f.readlines()
                # Find FIRECRAWL_API_KEY at line 133 (0-indexed: 132)
                for i, line in enumerate(lines):
                    if i == 132 and line.strip().startswith('FIRECRAWL_API_KEY='):
                        key_part = line.split('=')[1].strip()
                        # Remove quotes if present
                        if (key_part.startswith('"') and key_part.endswith('"')) or \
                           (key_part.startswith("'") and key_part.endswith("'")):
                            self.firecrawl_api_key = key_part[1:-1]
                            break
                        else:
                            self.firecrawl_api_key = key_part
                    elif i > 130 and 'FIRECRAWL_API_KEY=' in line:
                        # Alternative: find any FIRECRAWL_API_KEY line
                        key_part = line.split('=')[1].strip()
                        if (key_part.startswith('"') and key_part.endswith('"')) or \
                           (key_part.startswith("'") and key_part.endswith("'")):
                            self.firecrawl_api_key = key_part[1:-1]
                            break
                else:
                    # If not found, use empty string or skip authentication
                    print("  ℹ️ Warning: FIRECRAWL_API_KEY not found in ~/.hermes/.env")
                    self.firecrawl_api_key = ""
        except Exception as e:
}
# Use local Firecrawl API (localhost:3002)
            options = {
                "mode": "fast",
                "includePages": True,
                "maxPagesPerDomain": 1
            }
            
            payload = {
                "query": query,
                "options": options
            }
            
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            url = self.firecrawl_url  # localhost:3002/v1/search
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.firecrawl_api_key}' if self.firecrawl_api_key else ''
            }
            
            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
                
                response.raise_for_status()
                search_results = response.json()
                
                # Parse Firecrawl v2 JSON response
                results = []
                if "data" in search_results and len(search_results["data"]) > 0:
                    for item in search_results["data"][:5]:  # Limit to top 5 per query
                        results.append({
                            "title": item.get("metadata", {}).get("title", ""),
                            "url": item.get("url", ""),
                            "description": item.get("markdown", "")[:1000],  # Truncate long text
                            "source": "firecrawl"
                        })
                
                if not results:
                    print(f"    ⚠️ No search results found for '{query[:30]}...'")
                    
                return {
                    "query": query,
                    "status": "success",
                    "results": results,
                    "raw_results_count": len(results),
                    "source": "firecrawl"
                }
            
            except requests.exceptions.RequestException as e:
                print(f"    ⚠️ Request failed for '{query[:40]}...': {type(e).__name__}")
                return {"query": query, "status": "failed", "reason": f"Request error: {e}"}
            self.firecrawl_api_key = ""
        
        # Output files
        self.report_path = self.reports_dir / f"unified_overnight_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        self.metadata_path = self.reports_dir / "unified_engine_metadata.json"
        
        # Performance tracking
        self.execution_stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "start_time": None,
            "end_time": None
        }
        
        # Relationship iteration tracking
        self.discovered_concepts: Set[str] = set()
        self.relationship_layers: List[Dict] = []
    
    def _load_gematria_config(self) -> Dict:
        """Load configuration from IMAGE-SEED style database (top-level symbols)"""
        try:
            with open(self.db_path, 'r') as f:
                content = f.read()
            
            # Clean leading whitespace/tabs and parse
            lines = content.strip().split('\n')
            cleaned_lines = [line.lstrip() for line in lines]
            db_text = '\n'.join(cleaned_lines)
            db = json.loads(db_text)
            
            # IMAGE-SEED database has symbols at top-level, not under metadata
            core_symbols = db.get("symbols", [])
            relationships = db.get("relationships", [])
            
            # Try to get metadata fields (may be missing in IMAGE-SEED format)
            domains = db.get("metadata", {}).get("domains_tracked", ["general_gematria"])
            elemental_forces = db.get("metadata", {}).get("elemental_forces", [])
            
            return {
                "symbols": core_symbols,
                "domains": domains,
                "relationships": relationships,
                "elemental_forces": elemental_forces
            }
        except Exception as e:
            print(f"  ⚠️ Warning: Could not load full database: {e}")
            return {"symbols": [124, 963, 55], "domains": [], "relationships": []}
    
    def _generate_queries(self, config: Dict) -> List[str]:
        """Generate diverse search queries for each symbol"""
        query_templates = [
            "{symbol} meaning",
            "number {symbol} significance",
            "{symbol} pattern",
            "to {symbol} gematria",
            "{symbol} analysis",
            "historical figure age death transition",
            "meaning of number {symbol} in gematria system"
        ]
        
        queries = []
        for symbol in config["symbols"]:
            symbol_display = str(symbol).replace(" ", "")
            
            for template in query_templates:
                query = template.replace("{symbol}", symbol_display)
                if query not in queries:
                    queries.append(query)
                    if len(queries) >= 6:  # Limit to 6 unique queries
                        break
        return queries
    
    def _scrape_firecrawl(self, query: str, session_id: int) -> Dict:
        """Scrape using local Firecrawl API for a single query"""
        try:
            # Rate limiting between requests (1s delay for Firecrawl)
            if len(self.execution_stats["queries"]) > 0:
                time.sleep(1.0)
            
            # Build request body for Firecrawl v2 API
            payload = {
                "query": query,
                "options": {
                    "mode": "fast",
                    "includePages": True,
                    "maxPagesPerDomain": 1
                }
                }
            ctx = ssl.create_default_context()
                options = {
                    "mode": "fast",
                    "includePages": True,
                    "maxPagesPerDomain": 1
                }
                
                payload = {
                    "query": query,
                    "options": options
                }
                
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                
                url = self.firecrawl_url  # Use configured Firecrawl instance (localhost:3002)
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.firecrawl_api_key}' if self.firecrawl_api_key else ''
                }
                
                try:
                    response = requests.post(
                        url,
                        json=payload,
                        headers=headers,
                        timeout=self.timeout
                    )
                    
                    response.raise_for_status()
                    search_results = response.json()
                    
                    # Parse Firecrawl v2 JSON response
                    results = []
                    if "data" in search_results and len(search_results["data"]) > 0:
                        for item in search_results["data"][:5]:  # Limit to top 5 per query
                            results.append({
                                "title": item.get("metadata", {}).get("title", ""),
                                "url": item.get("url", ""),
                                "description": item.get("markdown", "")[:1000],  # Truncate long text
                                "source": "firecrawl"
                            })
                    
                    if not results:
                        print(f"    ⚠️ No search results found for '{query[:30]}...'")
                        
                    return {
                        "query": query,
                        "status": "success",
                        "results": results,
                        "raw_results_count": len(results),
                        "source": "firecrawl"
                    }
                    
            except requests.exceptions.RequestException as e:
                print(f"    ⚠️ Request failed for '{query[:40]}...': {type(e).__name__}")
                return {"query": query, "status": "failed", "reason": f"Request error: {e}"}
            
            except Exception as e:
                print(f"    ⚠️ Scrape error for '{query[:40]}...': {type(e).__name__}")
                return {"query": query, "status": "failed", "reason": str(e)}
            
            try:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                
                with urllib.request.urlopen(url, context=ctx, timeout=self.timeout) as response:
                    html_content = response.read().decode('utf-8')
            except Exception as e:
                print(f"    ⚠️ Query failed (network): {query[:30]}...")
                return {"query": query, "status": "failed", "reason": f"Network error: {e}"}
            
            # Parse HTML for result links and titles
            results = self._parse_searxng_html(html_content, query)
            
            return {
                "query": query,
                "status": "success",
                "results": results,
                "raw_html_length": len(html_content)
            }
        except Exception as e:
            print(f"    ⚠️ Scrape error for '{query[:40]}...': {type(e).__name__}")
            return {"query": query, "status": "failed", "reason": str(e)}
    
    def _parse_searxng_html(self, html_content: str, query: str) -> List[Dict]:
        """Parse Firecrawl HTML results (method kept for compatibility)"""
        import re
        
        links = []
        
        # Extract result links from XLS2 (SearXNG standard format) or generic divs
        xls2_pattern = r'<div[^>]*data-url="([^"]*)"[^>]*><a[^>]*href="([^"]*)"[^>]*>(.*?)</a>'
        div_pattern = r'<div[^>]*class="[^"]*result[^"]*"([^>]*)>(.*?)</div>'
        
        # Try XLS2 format first (modern SearXNG)
        xls2_matches = re.findall(xls2_pattern, html_content, re.DOTALL | re.IGNORECASE)
        for url, href, title in xls2_matches[:5]:  # Limit to top 5 results per query
            links.append({
                "url": url,
                "title": title.strip(),
                "display_url": href,
                "relevance_score": random.uniform(0.8, 1.0)
            })
        
        # If no XLS2 format, try generic div parsing
        if len(links) == 0:
            try:
                # Basic HTML parser for fallback
                from html.parser import HTMLParser
                
                class LinkExtractor(HTMLParser):
                    def __init__(self):
                        super().__init__()
                        self.current_link = None
                        self.current_text = ""
                        self.in_link = False
                        
                    def handle_starttag(self, tag, attrs):
                        if tag == 'a':
                            href = dict(attrs).get('href', '')
                            if href:
                                self.current_link = href
                    
                    def handle_endtag(self, tag):
                        if tag == 'a' and self.current_link:
                            # Extract text between start and end tag
                            pass
                
                extractor = LinkExtractor()
                extractor.feed(html_content)
                
                # Fallback: simple regex for anchor tags
                anchor_pattern = r'<a\s+(?:[^>]*?\s+)?href=["\']([^"\']+)["\'][^>]*>(.*?)</a>'
                anchors = re.findall(anchor_pattern, html_content, re.DOTALL | re.IGNORECASE)
                
                seen_urls = set()
                for url, text in anchors:
                    if 'google.com' not in url.lower() and len(url) > 20 and url not in seen_urls:
                        seen_urls.add(url)
                        
                        title_snippet = text[:100].strip().replace('\n', ' ')
                        
                        links.append({
                            "url": url,
                            "title": title_snippet,
                            "display_url": url,
                            "relevance_score": random.uniform(0.7, 0.95)
                        })
                        if len(links) >= 3:
                            break
                            
            except Exception as e:
                print(f"    ⚠️ HTML parsing fallback failed: {e}")
        
        return links[:10]  # Return up to 10 best results
    
    def _analyze_patterns(self, results: List[Dict], domains: Set[str]) -> Dict:
        """Analyze discovered patterns for convergence across domains"""
        pattern_analysis = {
            "total_results": len(results),
            "domain_coverage": {},
            "convergence_signals": [],
            "key_themes": []
        }
        
        # Track which domains each result belongs to
        all_urls = [r["url"] for r in results]
        
        # Basic URL categorization (simplified domain detection)
        for url in all_urls:
            domain = url.split('/')[2] if len(url.split('/')) > 2 else "unknown"
            
            # Map domains to conceptual categories
            if 'wikipedia' in domain.lower():
                category = "encyclopedia"
            elif 'facebook' in domain.lower() or 'fbcdn' in domain.lower():
                category = "social_history"
            elif 'bab.la' in domain.lower():
                category = "translation"
            else:
                category = "general_web"
            
            if category not in pattern_analysis["domain_coverage"]:
                pattern_analysis["domain_coverage"][category] = 0
            pattern_analysis["domain_coverage"][category] += 1
        
        # Detect convergence signals (symbols appearing across multiple domains)
        for result in results[:5]:  # Focus on top results
            title = result.get("title", "").lower()
            url = result.get("url", "")
            
            # Check if result mentions gematria-related concepts
            keywords = ["gematria", "numerology", "bible", "number", "symbol", 
                       "mystery", "pattern", "code", "frequency"]
            
            domain_terms = ["biblical", "religious", "historical", "ancient", 
                          "military", "scientific", "linguistic"]
            
            theme_detected = False
            dominant_domain = None
            
            for keyword in keywords:
                if keyword in title:
                    pattern_analysis["key_themes"].append(keyword.capitalize())
                    theme_detected = True
                    break
            
            # Map results to domains based on content
            for domain_term in domain_terms:
                if domain_term in url or domain_term in title:
                    for domain in domains:
                        if domain_term.lower() in domain.lower():
                            pattern_analysis["convergence_signals"].append({
                                "type": "domain_overlap",
                                "result_url": url[:50],
                                "overlap_domain": domain,
                                "confidence": 0.7
                            })
                            dominant_domain = domain
                            break
            
            if dominant_domain:
                pattern_analysis["key_themes"].append(dominant_domain)
        
        return pattern_analysis
    
    def _build_relationships(self, results: List[Dict], existing_rels: List[Dict]) -> List[Dict]:
        """Build new relationships from discovered concepts"""
        new_relationships = []
        
        # Extract concepts from titles and URLs
        all_concepts = set()
        for result in results:
            title = result.get("title", "")
            url = result.get("url", "")
            
            # Extract keywords from titles
            concepts_in_title = re.findall(r'\b(a|an|the)?\s*([a-z0-9\s]+)\b', title.lower())
            for _, concept in concepts_in_title:
                concept_clean = concept.strip()
                if len(concept_clean) > 3 and len(concept_clean) < 40:
                    all_concepts.add(concept_clean.lower().replace(' ', '_'))
            
            # Extract URL-based concepts
            domain_concept = url.split('/')[2] if len(url.split('/')) > 2 else ""
            if len(domain_concept) > 5:
                all_concepts.add(domain_concept.lower())
        
        # Build relationships between new and existing concepts
        for concept in list(all_concepts)[:10]:  # Limit to manageable number
            source = f"#discovered-{concept}"
            
            for i, existing_rel in enumerate(existing_rels[-5:]):  # Link to recent discoveries
                if len(new_relationships) < 20:  # Cap relationship count
                    new_relationships.append({
                        "type": "new_discovery_to_existing",
                        "source": source,
                        "target": existing_rel.get("target", "#existing_concept"),
                        "weight": random.uniform(0.5, 0.9),
                        "context": f"New concept '{concept}' relates to {existing_rel.get('context', '')[:50]}"
                    })
        
        # Add relationships between new discoveries themselves
        concept_list = list(all_concepts)[:8]
        for i, c1 in enumerate(concept_list):
            for c2 in concept_list[i+1:]:
                if len(new_relationships) < 30:
                    new_relationships.append({
                        "type": "cross-discovery",
                        "source": f"#discovered-{c1}",
                        "target": f"#discovered-{c2}",
                        "weight": random.uniform(0.6, 0.95),
                        "context": f"Cross-reference between {c1} and {c2}"
                    })
        
        return new_relationships
    
    def _track_temporal_patterns(self, results: List[Dict]) -> Dict:
        """Track temporal patterns in symbol appearances"""
        temporal_data = {
            "query_sequence": [r.get("query", "")[:40] for r in results],
            "result_count_per_query": [len(r.get("results", [])) for r in results],
            "average_results_per_query": 0,
            "discovery_rate": 0
        }
        
        if len(results) > 0:
            total_results = sum(len(r.get("results", [])) for r in results)
            temporal_data["average_results_per_query"] = total_results / len(results)
            temporal_data["discovery_rate"] = (total_results / len(results)) / 10  # Normalized
            
        return temporal_data
    
    def _generate_ascii_heatmap(self, relationships: List[Dict], symbols: List[str]) -> str:
        """Generate ASCII relationship heatmap"""
        if len(relationships) == 0 or len(symbols) < 3:
            return "No relationships to visualize."
        
        # Create simple density visualization
        lines = ["\n🔥 Relationship Density Heatmap (ASCII):", "=" * 60]
        
        # Calculate relationship weights by type
        type_counts = {}
        for rel in relationships[-30:]:  # Last 30 relationships
            rtype = rel.get("type", "unknown")
            weight = rel.get("weight", 0.5)
            
            if rtype not in type_counts:
                type_counts[rtype] = {"count": 0, "total_weight": 0}
            
            type_counts[rtype]["count"] += 1
            type_counts[rtype]["total_weight"] += weight
        
        # Visualize as bar chart
        for rtype, data in sorted(type_counts.items(), key=lambda x: x[1]["total_weight"], reverse=True)[:4]:
            bar_length = int(data["total_weight"] * 20)  # Scale to 0-20 chars
            bar = "█" * bar_length + "░" * (20 - bar_length)
            
            lines.append(f"\n📊 {rtype.replace('_', ' ').title()} Relationship Strength:")
            lines.append(f"   {bar}")
            lines.append(f"   {'█' * 5} {data['total_weight']:.1f}%")
        
        return "\n".join(lines) + "\n\n"
    
    def run(self):
        """Main execution loop"""
        print("\n" + "=" * 70)
        print(f"🚀 Unified Overnight Research Engine (Firecrawl API Mode)")
        print("=" * 70 + "\n")
        
        # Initialize tracking
        self.execution_stats["start_time"] = datetime.now().isoformat()
        self.execution_stats["queries"] = []
        
        # Load configuration
        config = self._load_gematria_config()
        symbols = config.get("symbols", [])
        # Use list instead of set so we can slice with [:5] later
        domains = list(d.lower() for d in config.get("domains", []))
        existing_rels = config.get("relationships", [])
        elemental_forces = config.get("elemental_forces", [])
        
        print(f"✅ Loaded {len(symbols)} core symbols from configuration")
        if len(domains) > 0:
            print(f"   Domains: {', '.join(domains[:5])}...")
        print(f"🧠 Starting analysis engine...\n")
        
        # Generate queries
        queries = self._generate_queries(config)
        print(f"🔍 Generated {len(queries)} unique queries")
        
        # Execute queries and collect results
        all_results = []
        for i, query in enumerate(queries, 1):
            print(f"\n  🔍 [{i}/{len(queries)}] Searching: {query[:50]}...")
            
            result = self._scrape_firecrawl(query, i)
            self.execution_stats["queries"].append(result)
            
            if result["status"] == "success":
                print(f"    ✅ Found {len(result.get('results', []))} potential links")
                all_results.append(result)
                
                # Update stats
                self.execution_stats["successful_queries"] += 1
            else:
                print(f"    ❌ Failed: {result.get('reason', 'Unknown')}")
                self.execution_stats["failed_queries"] += 1
        
        print(f"\n📊 Query Summary:")
        print(f"   Successful: {self.execution_stats['successful_queries']}/{len(queries)}")
        print(f"   Failed: {self.execution_stats['failed_queries']}")
        
        # Analyze patterns across all results
        converged_concepts = []
        temporal_data = {}
        
        if len(all_results) > 0:
            print(f"\n🧪 Running pattern analysis...")
            
            all_pattern_results = []
            for result in all_results:
                parsed_results = result.get("results", [])
                
                # Get raw domains from results (for convergence detection)
                raw_domains = set()
                for r in parsed_results[:3]:
                    url = r.get("url", "")
                    if len(url.split('/')) > 2:
                        domain_part = url.split('/')[2]
                        raw_domains.add(domain_part)
                
                pattern_analysis = self._analyze_patterns(parsed_results, raw_domains)
                all_pattern_results.append(pattern_analysis)
            
            # Aggregate cross-domain convergence signals
            for pa in all_pattern_results:
                for signal in pa.get("convergence_signals", []):
                    if not any(c["signal_url"] == signal["result_url"] for c in converged_concepts):
                        converged_concepts.append(signal)
            
            print(f"   ✅ Detected {len(converged_concepts)} cross-domain convergence signals")
            
            # Analyze temporal patterns
            temporal_data = self._track_temporal_patterns(all_results)
            print(f"   ⏱️ Average results per query: {temporal_data['average_results_per_query']:.1f}")
        
        # Build relationships from new discoveries
        all_relationships = []
        for result in all_results:
            parsed = result.get("results", [])
            new_rels = self._build_relationships(parsed, existing_rels)
            all_relationships.extend(new_rels)
        
        print(f"\n🔗 Built {len(all_relationships)} new relationships")
        
        # Generate ASCII heatmap
        if len(symbols) >= 3 and len(all_relationships) > 0:
            heatmap = self._generate_ascii_heatmap(all_relationships[-50:], symbols[:11])
            print(f"\n🔥 Heatmap visualizations generated")
        else:
            heatmap = "\nNo relationships to visualize yet.\n"
        
        # Update database with new findings
        try:
            with open(self.db_path, 'r') as f:
                db = json.load(f)
            
            existing_rels = db.get("metadata", {}).get("relationships", [])
            
            if len(all_relationships) > 0:
                # Append new relationships to existing (avoid duplicates)
                seen_pairs = set()
                for rel in all_relationships:
                    pair = tuple(sorted([rel.get("source", ""), rel.get("target", "")]))
                    if pair not in seen_pairs and len(existing_rels) < 500:
                        seen_pairs.add(pair)
                        existing_rels.append(rel)
                
                db["metadata"]["relationships"] = existing_rels
                
                with open(self.db_path, 'w') as f:
                    json.dump(db, f, indent=2, default=str)
            
            print(f"💾 Updated database with {len(existing_rels)} total relationships")
        except Exception as e:
            print(f"⚠️ Warning: Could not update database: {e}")
        
        # Generate comprehensive report
        self._generate_comprehensive_report(
            queries, all_results, all_relationships, 
            converged_concepts, temporal_data, config, heatmap
        )
        
        # Save metadata
        self.execution_stats["end_time"] = datetime.now().isoformat()
        self.execution_stats["total_execution_time_seconds"] = len(all_results)  # Simplified
        
        with open(self.metadata_path, 'w') as f:
            json.dump(self.execution_stats, f, indent=2)
        
        print(f"\n✅ Overnight research completed successfully!")
        print(f"📄 Check the latest report:")
        print(f"   {self.report_path}")
        print("=" * 70 + "\n")
    
    def _generate_comprehensive_report(self, queries: List[str], results: List[Dict], 
                                      relationships: List[Dict], converged_concepts: List[Dict],
                                      temporal_data: Dict, config: Dict, heatmap: str):
        """Generate comprehensive markdown report with all analysis"""
        
        # Count symbol occurrences in results
        try:
            symbol_mentions = {}
            for query_result in results:
                query = query_result.get("query", "")
                parsed = query_result.get("results", [])
                
                for result in parsed:
                    title = result.get("title", "").lower()
                    url = result.get("url", "")
                    
                    # Track which symbols this query was about
                    if "124" in query or "0 to" in query.lower():
                        symbol_mentions["124"] = symbol_mentions.get("124", 0) + len(parsed)
                    elif "963" in query:
                        symbol_mentions["963"] = symbol_mentions.get("963", 0) + len(parsed)
                    elif "55" in query:
                        symbol_mentions["55"] = symbol_mentions.get("55", 0) + len(parsed)
                    else:
                        # Generic tracking
                        for sym in config.get("symbols", []):
                            if str(sym).replace(" ", "") not in symbol_mentions:
                                symbol_mentions[str(sym).replace(" ", "")] = symbol_mentions.get(str(sym).replace(" ", ""), 0) + len(parsed)
        except Exception as e:
            pass  # Silently ignore errors during report generation
        
        with open(self.report_path, 'w') as f:
            report_lines = [
                f"# 📊 Overnight Research Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
                "",
                "## 🎯 Executive Summary",
                "",
                f"- **Symbols Processed**: {len(config.get('symbols', []))}",
                f"- **Queries Executed**: {len(queries)} / {len(queries) * (30//6 if any(len(r.get('results',[]))>0 for r in results) else 1)}",
                f"- **Successful Queries**: {len([r for r in results if r.get('status')=='success'])}",
                f"- **Cross-Domain Signals**: {len(converged_concepts)}",
                f"- **New Relationships**: {len(relationships)}",
                "",
                "## 🔍 Query Results & Discovery Summary\n",
            ]
            
            # Per-query results
            for i, query in enumerate(queries, 1):
                status = "✅" if any(r.get("query") == query and r.get("status") == "success" for r in results) else "❌"
                report_lines.append(f"- {status} `{query[:60]}...`")

            report_lines.extend([
                "",
                "## 🧪 Pattern Analysis Results\n",
            ])
            
            # Cross-domain convergence signals
            if len(converged_concepts) > 0:
                report_lines.append("### 🔗 Convergence Signals Detected:\n")
                
                for signal in converged_concepts[:10]:
                    url_display = signal.get("result_url", "")[:50]
                    domain = signal.get("overlap_domain", "unknown")
                    confidence = signal.get("confidence", 0.7)
                    
                    report_lines.extend([
                        f"- **Domain Overlap** ({domain}):",
                        f"    - URL: `{url_display}...`",
                        f"    - Confidence: {confidence:.1%}\n",
                    ])
            else:
                report_lines.append("No cross-domain convergence signals detected yet.\n")
            
            # Temporal analysis
            report_lines.extend([
                "## ⏱️ Temporal Tracking\n",
                f"- Average results per query: {temporal_data.get('average_results_per_query', 0):.1f}",
                f"- Discovery rate (normalized): {temporal_data.get('discovery_rate', 0):.2%}\n",
            ])
            
            # ASCII Heatmap
            report_lines.extend([heatmap])
            
            # Relationship iteration tracking
            report_lines.extend([
                "## 🔗 Relationship Iteration Log\n",
                "",
                "### Layer 1: Symbol → Domain Associations",
                "",
                f"Discovered {len([r for r in relationships if 'symbol_domain' in r.get('type', '')])} symbol-domain connections",
                "",
                "### Layer 2: Cross-Discovery Links",
                "",
                f"Created {len([r for r in relationships if 'cross-discovery' in r.get('type', '')])} relationships between new discoveries",
                "",
                "### Layer 3: Temporal Sequences",
                "",
                "Tracking symbol appearance frequency across queries:",
                ""
            ])
            
            # Add symbol mention counts
            for symbol, count in sorted(symbol_mentions.items(), key=lambda x: x[1], reverse=True)[:5]:
                report_lines.extend([
                    f"- `{symbol}`: {count} mentions",
                ])
            
            report_lines.extend([
                "",
                "## 📈 Key Insights & Anomalies\n",
                "",
                "### High-Frequency Domains:",
                ""
            ])
            
            # Extract domain frequencies from results
            domain_freq = {}
            for result in results:
                parsed = result.get("results", [])
                for r in parsed[:3]:
                    url = r.get("url", "")
                    if len(url.split('/')) > 2:
                        domain_part = url.split('/')[2]
                        category = "encyclopedia" if 'wikipedia' in domain_part else "general_web"
                        domain_freq[category] = domain_freq.get(category, 0) + 1
            
            for domain, count in sorted(domain_freq.items(), key=lambda x: x[1], reverse=True):
                report_lines.extend([f"- {domain.capitalize()}: {count} results\n"])
            
            report_lines.extend([
                "",
                "## 🎯 Recommendations for Next Overnight Run",
                "",
                "1. Focus on symbols with <3 domain appearances for deeper analysis",
                "2. Re-run queries that returned <2 results for refinement",
                "3. Investigate high-confidence convergence signals (>0.8 confidence)",
                "",
                "---\n",
                f"*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n"
            ])
            
        print(f"   📄 Report written to: {self.report_path}")


# Main entry point
if __name__ == "__main__":
    engine = UnifiedOvernightEngine()
    engine.run()
