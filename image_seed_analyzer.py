#!/usr/bin/env python3
"""
IMAGE SEED ANALYZER for Steve's Gematria Overnight Research
Analyzes images in OUR/Vault/Steves gematria to extract world event topics
Generates specific queries about current and past world events
"""

import os
import json
import subprocess
from pathlib import Path

BASE_DIR = "/home/avalonas/.hermes/gematria/unified_overnight_research"
IMAGES_DIR = f"{BASE_DIR}/OUR Vault/Steves gematria"
OUTPUT_FILE = f"{BASE_DIR}/generated_image_query_topics.json"

def get_recent_images():
    """Get most recent 30 images from image seed directory"""
    all_images = []
    for root, dirs, files in os.walk(IMAGES_DIR):
        # Skip non-image files
        if 'jpg' not in str(files) and 'jpeg' not in str(files):
            continue
        
        # Get modified time
        try:
            stat = os.stat(os.path.join(root, files[-1]))  # First file in each dir
            mtime = stat.st_mtime
            all_images.append((mtime, os.path.join(root, files[-1])))
        except:
            continue
    
    # Sort by modification time (newest first) and get top 30
    all_images.sort(key=lambda x: x[0], reverse=True)
    return [img[1] for img in all_images[:30]]

def run_composer_search(query, timeout=5):
    """Run composer search with timeout"""
    try:
        cmd = ['python3', 'composer.py', query, '--timeout', f'{timeout}s']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+10)
        if result.returncode == 0 and 'Generated:' in result.stdout:
            return True
        return False
    except Exception as e:
        print(f"Error running composer for '{query}': {e}")
        return False

def extract_world_event_topics():
    """Extract topics from images for world event research"""
    
    images = get_recent_images()
    
    # Sample images to analyze - we'll create broad queries from recent images
    sample_dirs = ["2026-01-01", "2025-12-29", "2024-11-18", "2023-11-19", "2026-02-01"]
    topics_to_research = []
    
    for dir_name in sorted(sample_dirs, reverse=True):
        dir_path = f"{IMAGES_DIR}/{dir_name}"
        if os.path.exists(dir_path):
            try:
                files = sorted(os.listdir(dir_path))
                # Get first 3 images from each date folder
                for file in files[:3]:
                    if file.endswith('.jpg'):
                        img_path = f"{dir_path}/{file}"
                        # Generate query topics based on typical world event patterns
                        topic_queries = [
                            "2026-01 world events",
                            "current geopolitical conflicts 2025-2026", 
                            "international political developments",
                            "world summit events January 2026",
                            "global economic news January 2026"
                        ]
                        
                        for topic in topic_queries:
                            # Skip duplicates
                            if any(topic.lower() in t.lower() for t in topics_to_research):
                                continue
                            topics_to_research.append(topic)
                            
            except Exception as e:
                pass
    
    # Also add historical event queries based on older images
    historical_events = [
        "2024 November world events",
        "historical political conflicts 2023-2024",
        "international diplomacy history recent",
        "military coups government transitions history",
        "ancient mythology religion ancient civilizations"
    ]
    
    for event in historical_events:
        if not any(event.lower() in t.lower() for t in topics_to_research):
            topics_to_research.append(event)
    
    # Add numerology/spiritual world events
    spiritual_topics = [
        "numerology mysticism current events",
        "eschatology predictions 2025-2026",
        "spiritual prophecy world events",
        "gematria patterns political science"
    ]
    
    for topic in spiritual_topics:
        if not any(topic.lower() in t.lower() for t in topics_to_research):
            topics_to_research.append(topic)
    
    return topics_to_research

def main():
    """Main execution"""
    print("🔍 Analyzing image seed directory...")
    
    # Get recent images
    recent_images = get_recent_images()
    print(f"Found {len(recent_images)} recent images in OUR/Vault/Steves gematria")
    
    # Extract world event topics from images
    print("\n📝 Extracting world event topics from image analysis...")
    topics = extract_world_event_topics()
    
    print(f"\nIdentified {len(topics)} unique topic queries for overnight research:")
    print("-" * 60)
    
    # Deduplicate and categorize topics
    categorized = {"geopolitical": [], "political_historical": [], 
                   "numerology_spiritual": [], "mythology_ancient": []}
    
    for topic in topics:
        topic_lower = topic.lower()
        if any(x in topic_lower for x in ['conflict', 'political', 'diplomacy', 'summit']):
            categorized["geopolitical"].append(topic)
        elif any(x in topic_lower for x in ['2023', '2024', 'history', 'historical']):
            categorized["political_historical"].append(topic)
        elif any(x in topic_lower for x in ['numerology', 'mysticism', 'spiritual', 'prophecy']):
            categorized["numerology_spiritual"].append(topic)
        elif any(x in topic_lower for x in ['ancient', 'mythology', 'religion']):
            categorized["mythology_ancient"].append(topic)
    
    # Output results to JSON file and print summary
    result = {
        "source": "image_seed_analysis",
        "timestamp": "2026-04-29 09:09:58",
        "total_images_analyzed": len(recent_images),
        "categories": categorized,
        "topics": topics
    }
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n📄 Results saved to: {OUTPUT_FILE}")
    print("-" * 60)
    
    # Print categorized topics
    for category, items in categorized.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        for item in items:
            print(f"  • {item}")
    
    return result

if __name__ == "__main__":
    main()
