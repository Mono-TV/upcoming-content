#!/usr/bin/env python3
"""
Add Playback Links to OTTPlay Content
Adds various watch/playback links based on available metadata:
- IMDb links
- TMDB links
- Platform-specific search links
- OTTPlay aggregator links
"""

import json
import urllib.parse
from datetime import datetime


def normalize_platform_name(platform):
    """Normalize platform names for link construction"""
    if not platform:
        return None

    platform_lower = platform.lower()

    # Map to standard names
    if 'netflix' in platform_lower:
        return 'Netflix'
    elif 'prime' in platform_lower or 'amazon' in platform_lower:
        return 'Amazon Prime Video'
    elif 'hotstar' in platform_lower:
        return 'Hotstar'
    elif 'zee5' in platform_lower or 'zee 5' in platform_lower:
        return 'Zee5'
    elif 'sony' in platform_lower:
        return 'Sony LIV'
    elif 'apple' in platform_lower:
        return 'Apple TV+'
    elif 'sun' in platform_lower:
        return 'Sun NXT'
    elif 'aha' in platform_lower:
        return 'Aha'
    elif 'manorama' in platform_lower:
        return 'Manorama MAX'

    return platform


def get_platform_search_link(platform, title, imdb_id=None):
    """Generate platform-specific search link"""
    if not platform or not title:
        return None

    platform = normalize_platform_name(platform)
    encoded_title = urllib.parse.quote(title)

    # Platform-specific search URLs
    platform_urls = {
        'Netflix': f'https://www.netflix.com/search?q={encoded_title}',
        'Amazon Prime Video': f'https://www.primevideo.com/search/ref=atv_nb_sr?phrase={encoded_title}',
        'Hotstar': f'https://www.hotstar.com/in/search/{encoded_title}',
        'Zee5': f'https://www.zee5.com/search?q={encoded_title}',
        'Sony LIV': f'https://www.sonyliv.com/search/{encoded_title}',
        'Apple TV+': f'https://tv.apple.com/search?q={encoded_title}',
        'Sun NXT': f'https://www.sunnxt.com/search?q={encoded_title}',
        'Aha': f'https://www.aha.video/search?query={encoded_title}',
        'Manorama MAX': f'https://www.manoramamax.com/search?q={encoded_title}'
    }

    return platform_urls.get(platform)


def add_playback_links(input_file='ottplay_complete_enriched.json', output_file=None):
    """Add playback links to all items"""

    print("\n" + "="*70)
    print("ADDING PLAYBACK LINKS TO OTTPLAY CONTENT")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")

    # Load data
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    content = data.get('content', [])
    print(f"✓ Loaded {len(content)} items from {input_file}\n")

    enriched_count = 0

    for i, item in enumerate(content, 1):
        title = item.get('title', 'Unknown')
        added_links = []

        # Initialize watch_links dict
        if 'watch_links' not in item:
            item['watch_links'] = {}

        # Add IMDb link
        imdb_id = item.get('imdb_id')
        if imdb_id:
            item['watch_links']['imdb'] = f"https://www.imdb.com/title/{imdb_id}/"
            added_links.append('IMDb')

        # Add TMDB link
        tmdb_id = item.get('tmdb_id')
        tmdb_type = item.get('tmdb_media_type', 'movie')
        if tmdb_id:
            item['watch_links']['tmdb'] = f"https://www.themoviedb.org/{tmdb_type}/{tmdb_id}"
            added_links.append('TMDB')

        # Add OTTPlay link (already exists as 'link')
        ottplay_link = item.get('link')
        if ottplay_link:
            item['watch_links']['ottplay'] = ottplay_link
            if 'OTTPlay' not in added_links:
                added_links.append('OTTPlay')

        # Add platform-specific search link
        platform = item.get('content_provider')
        if platform:
            platform_link = get_platform_search_link(platform, title, imdb_id)
            if platform_link:
                normalized_platform = normalize_platform_name(platform)
                platform_key = normalized_platform.lower().replace(' ', '_')
                item['watch_links'][f'{platform_key}_search'] = platform_link
                added_links.append(f'{normalized_platform} Search')

        if added_links:
            enriched_count += 1
            if i % 50 == 0 or i <= 10:
                print(f"[{i}/{len(content)}] {title[:45]:45} → Added: {', '.join(added_links)}")

    # Update data
    data['content'] = content
    data['enriched_at'] = datetime.now().isoformat()

    # Save
    output_file = output_file or input_file

    # Create backup
    backup_file = f"{output_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"\n💾 Creating backup: {backup_file}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        with open(input_file, 'r', encoding='utf-8') as original:
            f.write(original.read())

    # Save enriched data
    print(f"💾 Saving enriched data to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("\n" + "="*70)
    print("✅ PLAYBACK LINKS ADDED!")
    print("="*70)
    print(f"\n📊 Results:")
    print(f"   • Items enriched with watch links: {enriched_count}/{len(content)}")
    print(f"   • Average links per item: {sum(len(item.get('watch_links', {})) for item in content) / len(content):.1f}")
    print(f"\n📁 Updated file: {output_file}")
    print("="*70 + "\n")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Add playback/watch links to OTTPlay content')
    parser.add_argument('--input', default='ottplay_complete_enriched.json',
                        help='Input JSON file (default: ottplay_complete_enriched.json)')
    parser.add_argument('--output', help='Output JSON file (default: same as input)')

    args = parser.parse_args()

    add_playback_links(args.input, args.output)
