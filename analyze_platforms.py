#!/usr/bin/env python3
"""
Comprehensive platform analysis for duplicates and inconsistencies
across all data sources and configuration files
"""

import json
import re
from collections import defaultdict

def analyze_script_js():
    """Extract platform names from script.js platformLogos"""
    platforms = []

    try:
        with open('script.js', 'r') as f:
            content = f.read()

        # Extract platform names from the platformLogos object
        in_platform_logos = False
        for line in content.split('\n'):
            if 'const platformLogos = {' in line:
                in_platform_logos = True
                continue
            if in_platform_logos:
                if line.strip().startswith("'") and ':' in line:
                    # Extract platform name
                    platform = line.strip().split("'")[1]
                    if not platform.startswith('Platform '):  # Skip numbered platforms
                        platforms.append(platform)
                elif '// Platform number references' in line:
                    break
    except FileNotFoundError:
        pass

    return platforms

def analyze_config_py():
    """Extract platform names from config.py"""
    platforms = {
        'BINGED_CONFIG': [],
        'OTT_PLATFORM_FILTERS': []
    }

    try:
        with open('config.py', 'r') as f:
            content = f.read()

        # Extract BINGED_CONFIG platforms
        binged_pattern = r"'platforms':\s*\{([^}]+)\}"
        match = re.search(binged_pattern, content, re.DOTALL)
        if match:
            for line in match.group(1).split('\n'):
                if ':' in line and "'" in line:
                    platform_name = line.split(':')[1].strip().strip(',').strip("'")
                    if platform_name:
                        platforms['BINGED_CONFIG'].append(platform_name)

        # Extract OTT_PLATFORM_FILTERS
        ott_pattern = r"OTT_PLATFORM_FILTERS = \[([^\]]+)\]"
        match = re.search(ott_pattern, content, re.DOTALL)
        if match:
            for line in match.group(1).split('\n'):
                if "'" in line:
                    platform_name = line.strip().strip(',').strip("'")
                    if platform_name:
                        platforms['OTT_PLATFORM_FILTERS'].append(platform_name)
    except FileNotFoundError:
        pass

    return platforms

def analyze_json_data():
    """Analyze platforms in actual JSON data files"""
    platforms_by_file = {}

    json_files = [
        'movies_enriched.json',
        'ott_releases_enriched.json',
        'theatre_current_enriched.json',
        'theatre_upcoming_enriched.json'
    ]

    for filename in json_files:
        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            platform_set = set()
            duplicates_in_items = []

            for item in data:
                if 'platforms' in item and item['platforms']:
                    # Check for duplicates within each item
                    if len(item['platforms']) != len(set(item['platforms'])):
                        duplicates_in_items.append({
                            'title': item.get('title', 'Unknown'),
                            'platforms': item['platforms']
                        })

                    for platform in item['platforms']:
                        platform_set.add(platform)

            platforms_by_file[filename] = {
                'unique_platforms': sorted(platform_set),
                'duplicates_in_items': duplicates_in_items
            }
        except FileNotFoundError:
            platforms_by_file[filename] = {
                'unique_platforms': [],
                'duplicates_in_items': []
            }

    return platforms_by_file

def find_duplicates(platforms):
    """Find duplicate or similar platform names using normalization"""
    duplicates = []
    normalized = defaultdict(list)

    for platform in platforms:
        # Normalize: lowercase, remove spaces, remove special chars
        key = platform.lower().replace(' ', '').replace('+', '').replace('-', '')
        normalized[key].append(platform)

    for key, variants in normalized.items():
        if len(variants) > 1:
            duplicates.append({
                'normalized': key,
                'variants': sorted(set(variants))
            })

    return duplicates

def main():
    print("=" * 80)
    print("COMPREHENSIVE PLATFORM FILTER ANALYSIS")
    print("=" * 80)

    # Analyze script.js
    print("\n1. PLATFORMS IN script.js (platformLogos)")
    print("-" * 80)
    script_platforms = analyze_script_js()
    print(f"Total platforms: {len(script_platforms)}")

    # Find duplicates in script.js
    script_duplicates = find_duplicates(script_platforms)
    if script_duplicates:
        print("\n⚠️  DUPLICATES FOUND in script.js:")
        for dup in script_duplicates:
            print(f"   • {', '.join(dup['variants'])} → normalized: '{dup['normalized']}'")
    else:
        print("✓ No duplicates found in script.js")

    # Analyze config.py
    print("\n\n2. PLATFORMS IN config.py")
    print("-" * 80)
    config_platforms = analyze_config_py()

    print(f"\nBINGED_CONFIG platforms ({len(config_platforms['BINGED_CONFIG'])}):")
    for p in sorted(config_platforms['BINGED_CONFIG']):
        print(f"   • {p}")

    print(f"\nOTT_PLATFORM_FILTERS ({len(config_platforms['OTT_PLATFORM_FILTERS'])}):")
    for p in sorted(config_platforms['OTT_PLATFORM_FILTERS']):
        print(f"   • {p}")

    # Check for duplicates in config.py
    all_config = config_platforms['BINGED_CONFIG'] + config_platforms['OTT_PLATFORM_FILTERS']
    config_duplicates = find_duplicates(all_config)
    if config_duplicates:
        print("\n⚠️  DUPLICATES FOUND in config.py:")
        for dup in config_duplicates:
            print(f"   • {', '.join(dup['variants'])} → normalized: '{dup['normalized']}'")
    else:
        print("\n✓ No duplicates found in config.py")

    # Analyze JSON data
    print("\n\n3. PLATFORMS IN JSON DATA FILES")
    print("-" * 80)
    json_platforms = analyze_json_data()

    all_json_platforms = []
    for filename, data in json_platforms.items():
        platforms = data['unique_platforms']
        duplicates = data['duplicates_in_items']

        print(f"\n{filename}:")
        print(f"   Unique platforms: {len(platforms)}")

        if duplicates:
            print(f"   ⚠️  Items with duplicate platforms: {len(duplicates)}")
            for item in duplicates[:3]:  # Show first 3
                print(f"      • \"{item['title']}\": {item['platforms']}")
            if len(duplicates) > 3:
                print(f"      ... and {len(duplicates) - 3} more")
        else:
            print(f"   ✓ No duplicate platforms within individual items")

        all_json_platforms.extend(platforms)

    # Check for duplicates across all JSON data
    json_duplicates = find_duplicates(set(all_json_platforms))
    if json_duplicates:
        print("\n⚠️  DUPLICATES FOUND across all JSON data:")
        for dup in json_duplicates:
            print(f"   • {', '.join(dup['variants'])} → normalized: '{dup['normalized']}'")

    # Cross-reference analysis
    print("\n\n4. CROSS-REFERENCE ANALYSIS")
    print("-" * 80)

    # Platforms in script.js but not in config
    script_set = set(script_platforms)
    config_set = set(all_config)

    only_in_script = script_set - config_set
    only_in_config = config_set - script_set

    if only_in_script:
        print(f"\nPlatforms in script.js but NOT in config.py ({len(only_in_script)}):")
        for p in sorted(only_in_script)[:20]:
            print(f"   • {p}")
        if len(only_in_script) > 20:
            print(f"   ... and {len(only_in_script) - 20} more")
    else:
        print("\n✓ All script.js platforms are in config.py")

    if only_in_config:
        print(f"\nPlatforms in config.py but NOT in script.js ({len(only_in_config)}):")
        for p in sorted(only_in_config):
            print(f"   • {p}")
    else:
        print("\n✓ All config.py platforms are in script.js")

    # Summary
    print("\n\n" + "=" * 80)
    print("SUMMARY OF ISSUES")
    print("=" * 80)

    total_issues = len(script_duplicates) + len(config_duplicates) + len(json_duplicates or [])

    if script_duplicates:
        print(f"\n⚠️  {len(script_duplicates)} duplicate(s) in script.js:")
        for dup in script_duplicates:
            print(f"   • {', '.join(dup['variants'])}")

    if config_duplicates:
        print(f"\n⚠️  {len(config_duplicates)} duplicate(s) in config.py:")
        for dup in config_duplicates:
            print(f"   • {', '.join(dup['variants'])}")

    if json_duplicates:
        print(f"\n⚠️  {len(json_duplicates)} duplicate(s) in JSON data:")
        for dup in json_duplicates:
            print(f"   • {', '.join(dup['variants'])}")

    if total_issues == 0:
        print("\n✓ No duplicates or naming inconsistencies found!")
    else:
        print(f"\n⚠️  Total: {total_issues} duplicate/inconsistency issue(s) found")

    print("\n")

if __name__ == '__main__':
    main()
