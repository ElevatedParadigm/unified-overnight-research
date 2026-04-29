#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STEVE'S GEMATRIA COMPOSER - Composer.py
Orchestrator for overnight research using local Firecrawl v1.9.0 and SearXNG-Clean

This script orchestrates the full overnight research pipeline, leveraging:
- Local Firecrawl (preferred) at http://localhost:3002/v1/search
- Cloud Firecrawl (fallback) at https://api.firecrawl.dev/v1
- SearXNG-Clean at http://localhost:8084/search

All services are configured to support core gematria symbols: 124, 963, 55, 111, 279, 666
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import requests
from urllib.parse import urljoin

# Configuration
LOCAL_FIRECRAWL_URL = "http://localhost:3002/v1/search"
CLOUD_FIRECRAWL_URL = "https://api.firecrawl.dev/v1"  # Alternative if local fails
SEARXNG_URL = "http://localhost:8084/search"
FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY", "")
USE_DB_AUTHENTICATION = False

# Core symbols to track
CORE_SYMBOLS = [124, 963, 55, 111, 279, 666]
EXTENDED_SYMBOLS = [285, 6966]


class Composer:
    """Orchestrator for overnight research workflow."""
    
    def __init__(self):
        self.session = requests.Session()
        self.local_api_base_url = LOCAL_FIRECRAWL_URL
        self.cloud_api_base_url = CLOUD_FIRECRAWL_URL
        self.searxng_base_url = SEARXNG_URL
    
    def log(self, message: str, level: str = "INFO") -> None:
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def check_service_health(self, url: str) -> bool:
        """Check if a service is healthy."""
        try:
            if "/health" in url:
                response = self.session.get(url, timeout=5)
                return response.status_code == 200 or "healthy" in response.text.lower()
            
            # For /v1/search endpoints, test with a simple query
            test_data = {"query": "test"}
            if url.startswith("http://localhost") or url.startswith("http://127.0.0.1"):
                # Local API
                response = self.session.post(url, json=test_data, timeout=10)
                return response.status_code in [200, 401]  # 401 is OK for auth-only APIs
            
            else:
                # Cloud or SearXNG
                if "/search" in url and "format=json" not in url:
                    params = {"q": "test", "format": "json"}
                    response = self.session.get(url, params=params, timeout=10)
                else:
                    data = {"query": "test"}
                    response = self.session.post(url, json=data, timeout=10)
                return response.status_code == 200
                
        except Exception as e:
            self.log(f"Health check failed for {url}: {e}", "WARNING")
            return False
    
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
        
        for symbol in CORE_SYMBOLS + EXTENDED_SYMBOLS:
            # Look for direct mentions
            if f"[{symbol}]" in content or f"({symbol})" in content or str(symbol) in content:
                # Extract context window
                idx = content.find(str(symbol))
                start = max(0, idx - 100)
                end = min(len(content), idx + 150)
                found.append({
                    "symbol": symbol,
                    "context": content[start:end],
                    "match": str(symbol)
                })
        
        return found
    
    def generate_oversight_report(self, search_results: Dict[str, Any], query: str) -> str:
        """Generate oversight report from search results."""
        # Check all available sources
        health_status = {
            "local_firecrawl": self.check_service_health(self.local_api_base_url),
            "searxng": self.check_service_health(self.searxng_base_url)
        }
        
        report_lines = [
            "=" * 70,
            "GEMATRIA OVERSIGHT REPORT",
            f"Query: {query[:100]}{'...' if len(query) > 100 else ''}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 70,
            "",
            "SERVICE HEALTH:",
        ]
        
        for service, healthy in health_status.items():
            status = "✅ ONLINE" if healthy else "⚠️ OFFLINE"
            report_lines.append(f"  {service}: {status}")
        
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
            "RECOMMENDATION:",
            "1. Review search results for pattern convergence",
            "2. Track emerging relationships between domains",
            "3. Update CROSS_REFERENCE_INDEX.md with new connections",
            f"4. Process {len(data) if isinstance(data, list) else data.get('scrapeResultsCount', len(search_results.get('results', [])))} items for analysis",
            "=" * 70,
        ])
        
        return "\n".join(report_lines)


def main():
    """Main entry point for Composer."""
    
    # Initialize composer
    composer = Composer()
    
    # Parse command line args
    query = sys.argv[1] if len(sys.argv) > 1 else "gematria patterns core symbols"
    
    print("=" * 70)
    print("STEVE'S GEMATRIA COMPOSER")
    print("=" * 70)
    print(f"\nSearch Query: {query}")
    print(f"\nAvailable Backend Services:")
    print(f"  • SearXNG-Clean (primary): http://localhost:8084/search")
    print(f"  • Firecrawl Local:        http://localhost:3002/v1/search")
    print(f"  • Firecrawl Cloud:        https://api.firecrawl.dev/v1 (fallback)")
    print()
    
    # Search
    results = composer.search_firecrawl_local(query)
    
    # Generate oversight report
    if "error" in results:
        print(f"\n⚠️ Error: {results['error']}")
        return 1
    
    report = composer.generate_oversight_report(results, query)
    print(report)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
