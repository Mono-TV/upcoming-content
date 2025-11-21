#!/usr/bin/env python3
"""
Fix poster languages - prioritize English and Indian language posters
over non-English/non-Indian language posters (Korean, Japanese, Chinese, etc.)
"""

import json
import os
import requests
import time

TMDB_API_KEY = os.environ.get('TMDB_API_KEY', '452357e5da52e2ddde20c64414a40637')

# Preferred languages (in priority order)
PREFERRED_LANGUAGES = [
    'en',  # English (highest priority)
    'hi',  # Hindi
    'ta',  # Tamil
    'te',  # Telugu
    'ml',  # Malayalam
    'kn',  # Kannada
    'bn',  # Bengali
    'mr',  # Marathi
    'pa',  # Punjabi
    'gu',  # Gujarati
    None,  # No language (often English posters without text)
]

# Languages to avoid (non-English, non-Indian)
AVOID_LANGUAGES = [
    'ko',  # Korean
    'ja',  # Japanese
    'zh',  # Chinese
    'th',  # Thai
    'vi',  # Vietnamese
    'id',  # Indonesian
    'ru',  # Russian
    'fr',  # French
    'de',  # German
    'es',  # Spanish
    'pt',  # Portuguese
    'it',  # Italian
]

def get_tmdb_posters_with_language(tmdb_id, media_type):
    """Get posters from TMDB with language metadata"""
    for attempt in range(3):
        try:
            url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/images"
            params = {'api_key': TMDB_API_KEY}

            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            posters = data.get('posters', [])

            # Return posters with their metadata
            return [{
                'file_path': img['file_path'],
                'language': img.get('iso_639_1'),  # Language code
                'vote_average': img.get('vote_average', 0),
                'vote_count': img.get('vote_count', 0)
            } for img in posters if img.get('file_path')]
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
                continue
            print(f"    Error: {e}")
            return []
    return []

def filter_and_sort_posters(posters):
    """
    Filter and sort posters by language preference
    Priority:
    1. English posters
    2. Indian language posters (Hindi, Tamil, Telugu, etc.)
    3. No language tag (often English without text)
    4. Avoid non-English/non-Indian languages
    """

    # Separate posters by preference
    preferred_posters = []
    avoid_posters = []

    for poster in posters:
        lang = poster['language']

        if lang in AVOID_LANGUAGES:
            avoid_posters.append(poster)
        elif lang in PREFERRED_LANGUAGES or lang is None:
            # Add language priority score
            if lang in PREFERRED_LANGUAGES:
                poster['lang_priority'] = PREFERRED_LANGUAGES.index(lang)
            else:
                poster['lang_priority'] = len(PREFERRED_LANGUAGES)
            preferred_posters.append(poster)
        else:
            # Unknown language - add to avoid list
            avoid_posters.append(poster)

    # Sort preferred posters by:
    # 1. Language priority (English first, then Hindi, etc.)
    # 2. Vote average (quality)
    preferred_posters.sort(key=lambda x: (x['lang_priority'], -x['vote_average']))

    # If no preferred posters, use avoid list sorted by quality
    if not preferred_posters:
        avoid_posters.sort(key=lambda x: -x['vote_average'])
        return avoid_posters

    return preferred_posters

def fix_poster_languages(filename):
    """Fix poster languages for a given JSON file"""

    # Load data
    with open(filename, 'r', encoding='utf-8') as f:
        movies = json.load(f)

    print(f"\n{'='*70}")
    print(f"FIXING POSTER LANGUAGES: {filename}")
    print(f"{'='*70}\n")
    print(f"Total movies: {len(movies)}\n")

    if not movies:
        print("No movies to process")
        return

    fixed_count = 0
    checked_count = 0

    for i, movie in enumerate(movies, 1):
        title = movie.get('title', 'Unknown')

        if not movie.get('tmdb_id') or not movie.get('tmdb_media_type'):
            continue

        checked_count += 1
        tmdb_id = movie['tmdb_id']
        media_type = movie['tmdb_media_type']

        print(f"[{i}/{len(movies)}] {title[:45]}... ", end='', flush=True)

        # Get all posters with language info
        posters = get_tmdb_posters_with_language(tmdb_id, media_type)

        if not posters:
            print("⊙ No posters available")
            continue

        # Filter and sort by language preference
        preferred_posters = filter_and_sort_posters(posters)

        if not preferred_posters:
            print("⊙ No suitable posters found")
            continue

        # Get current poster to check if we need to update
        current_poster = movie.get('posters', {}).get('medium', '')
        new_poster_path = preferred_posters[0]['file_path']
        new_poster_url = f"https://image.tmdb.org/t/p/w342{new_poster_path}"

        # Check if poster changed
        if new_poster_path in current_poster:
            lang = preferred_posters[0]['language'] or 'none'
            print(f"✓ Already optimal ({lang})")
            continue

        # Update with language-appropriate posters
        movie['posters'] = {
            'thumbnail': f"https://image.tmdb.org/t/p/w92{new_poster_path}",
            'small': f"https://image.tmdb.org/t/p/w185{new_poster_path}",
            'medium': f"https://image.tmdb.org/t/p/w342{new_poster_path}",
            'large': f"https://image.tmdb.org/t/p/w500{new_poster_path}",
            'xlarge': f"https://image.tmdb.org/t/p/w780{new_poster_path}",
            'original': f"https://image.tmdb.org/t/p/original{new_poster_path}"
        }

        # Store all preferred posters (up to 5)
        movie['all_posters'] = [
            {
                'thumbnail': f"https://image.tmdb.org/t/p/w92{p['file_path']}",
                'small': f"https://image.tmdb.org/t/p/w185{p['file_path']}",
                'medium': f"https://image.tmdb.org/t/p/w342{p['file_path']}",
                'large': f"https://image.tmdb.org/t/p/w500{p['file_path']}",
                'xlarge': f"https://image.tmdb.org/t/p/w780{p['file_path']}",
                'original': f"https://image.tmdb.org/t/p/original{p['file_path']}",
                'language': p['language']
            }
            for p in preferred_posters[:5]
        ]

        movie['poster_url_medium'] = movie['posters']['medium']
        movie['poster_url_large'] = movie['posters']['large']

        # Store poster language for reference
        movie['poster_language'] = preferred_posters[0]['language'] or 'none'

        old_lang = 'unknown'
        new_lang = preferred_posters[0]['language'] or 'none'

        fixed_count += 1
        print(f"✓ Updated to {new_lang} poster ({len(preferred_posters)} available)")

        time.sleep(0.3)  # Rate limiting

    # Save updated data
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(movies, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*70}")
    print(f"✅ Checked {checked_count} movies, updated {fixed_count} posters")
    print(f"💾 Saved: {filename}")
    print(f"{'='*70}\n")

def main():
    """Fix poster languages in all data files"""

    files_to_process = [
        'movies_enriched.json',
        'ott_releases_enriched.json',
        'theatre_current_enriched.json',
        'theatre_upcoming_enriched.json'
    ]

    total_checked = 0
    total_fixed = 0

    for filename in files_to_process:
        if os.path.exists(filename):
            try:
                with open(filename) as f:
                    data = json.load(f)
                if data:  # Only process if file has data
                    fix_poster_languages(filename)
            except Exception as e:
                print(f"\n⚠️  Error processing {filename}: {e}\n")

    print(f"\n{'='*70}")
    print(f"ALL POSTER LANGUAGES FIXED!")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    main()
