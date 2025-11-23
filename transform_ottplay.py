#!/usr/bin/env python3
"""
Transform OTTPlay enriched data to match the webpage format

Input: ottplay_complete_enriched.json (wrapped with metadata)
Output: ottplay_releases.json (direct array like other data files)
"""

import json
from datetime import datetime


def transform_ottplay_data():
    """Transform ottplay data to match the expected webpage format"""

    # Load the enriched ottplay data
    with open('ottplay_complete_enriched.json', 'r', encoding='utf-8') as f:
        ottplay_data = json.load(f)

    # Extract the content array
    content_items = ottplay_data.get('content', [])

    print(f"✓ Loaded {len(content_items)} items from ottplay_complete_enriched.json")

    # Transform each item to match the expected format
    transformed_items = []

    for item in content_items:
        # Skip items without posters (they won't display well on the website)
        if not item.get('posters') and not item.get('poster_url_medium'):
            continue

        # Map content_provider to platforms array
        platforms = []
        provider = item.get('content_provider', '')
        if provider:
            platforms = [provider]

        # Create transformed item
        transformed = {
            'content_type': 'ott_released',  # All ottplay content is released OTT content
            'title': item.get('title', 'Untitled'),
            'url': item.get('link', ''),
            'release_date': item.get('streaming_date', 'TBA'),
            'platforms': platforms,
            'image_url': item.get('poster_url_large') or item.get('poster_url_medium') or item.get('image_url', ''),
        }

        # Add deeplinks if available (none in current data, but structure is ready)
        if item.get('deeplinks'):
            transformed['deeplinks'] = item.get('deeplinks')

        # Add enriched TMDB/IMDB data if available
        if item.get('tmdb_id'):
            transformed['tmdb_id'] = item.get('tmdb_id')

        if item.get('tmdb_media_type'):
            transformed['tmdb_media_type'] = item.get('tmdb_media_type')

        if item.get('overview'):
            transformed['overview'] = item.get('overview')
            transformed['description'] = item.get('overview')
        elif item.get('description'):
            # Use existing description if no TMDB overview
            transformed['description'] = item.get('description')

        if item.get('genres'):
            transformed['genres'] = item.get('genres')

        if item.get('runtime'):
            transformed['runtime'] = item.get('runtime')

        if item.get('tmdb_release_date'):
            transformed['tmdb_release_date'] = item.get('tmdb_release_date')

        if item.get('status'):
            transformed['status'] = item.get('status')

        if item.get('tmdb_rating'):
            transformed['tmdb_rating'] = item.get('tmdb_rating')

        if item.get('tmdb_vote_count'):
            transformed['tmdb_vote_count'] = item.get('tmdb_vote_count')

        if item.get('original_title'):
            transformed['original_title'] = item.get('original_title')

        if item.get('original_language'):
            transformed['original_language'] = item.get('original_language')

        if item.get('imdb_id'):
            transformed['imdb_id'] = item.get('imdb_id')

        if item.get('imdb_rating'):
            transformed['imdb_rating'] = item.get('imdb_rating')

        if item.get('posters'):
            transformed['posters'] = item.get('posters')

        if item.get('all_posters'):
            transformed['all_posters'] = item.get('all_posters')

        if item.get('poster_url_medium'):
            transformed['poster_url_medium'] = item.get('poster_url_medium')

        if item.get('poster_url_large'):
            transformed['poster_url_large'] = item.get('poster_url_large')

        if item.get('poster_source'):
            transformed['poster_source'] = item.get('poster_source')

        if item.get('backdrops'):
            transformed['backdrops'] = item.get('backdrops')

        if item.get('all_backdrops'):
            transformed['all_backdrops'] = item.get('all_backdrops')

        if item.get('backdrop_url'):
            transformed['backdrop_url'] = item.get('backdrop_url')

        if item.get('cast'):
            transformed['cast'] = item.get('cast')

        if item.get('directors'):
            transformed['directors'] = item.get('directors')

        if item.get('writers'):
            transformed['writers'] = item.get('writers')

        if item.get('youtube_id'):
            transformed['youtube_id'] = item.get('youtube_id')

        if item.get('youtube_url'):
            transformed['youtube_url'] = item.get('youtube_url')

        if item.get('youtube_title'):
            transformed['youtube_title'] = item.get('youtube_title')

        if item.get('year'):
            transformed['year'] = item.get('year')

        if item.get('cbfc_rating'):
            transformed['cbfc_rating'] = item.get('cbfc_rating')

        transformed_items.append(transformed)

    print(f"✓ Transformed {len(transformed_items)} items (skipped {len(content_items) - len(transformed_items)} without posters)")

    # Save the transformed data
    with open('ottplay_releases.json', 'w', encoding='utf-8') as f:
        json.dump(transformed_items, f, indent=2, ensure_ascii=False)

    print(f"💾 Saved: ottplay_releases.json")

    # Summary
    with_posters = sum(1 for item in transformed_items if item.get('posters'))
    with_tmdb = sum(1 for item in transformed_items if item.get('tmdb_id'))
    with_imdb = sum(1 for item in transformed_items if item.get('imdb_id'))
    with_platforms = sum(1 for item in transformed_items if item.get('platforms'))

    print(f"\n📊 Summary:")
    print(f"   • Total items: {len(transformed_items)}")
    print(f"   • With posters: {with_posters}/{len(transformed_items)}")
    print(f"   • With TMDB IDs: {with_tmdb}/{len(transformed_items)}")
    print(f"   • With IMDB IDs: {with_imdb}/{len(transformed_items)}")
    print(f"   • With platforms: {with_platforms}/{len(transformed_items)}")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("OTTPLAY DATA TRANSFORMER")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

    transform_ottplay_data()

    print("\n" + "="*60)
    print("✅ TRANSFORMATION COMPLETE")
    print("="*60 + "\n")
