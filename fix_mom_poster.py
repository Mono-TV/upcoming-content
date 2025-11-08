#!/usr/bin/env python3
"""
Fix Mom (2017) poster by fetching from TMDb API
"""

import json
import os
import requests

def main():
    tmdb_api_key = os.environ.get('TMDB_API_KEY')

    if not tmdb_api_key:
        print('❌ TMDB_API_KEY not set')
        print('Please set it: export TMDB_API_KEY="your_key"')
        print('Get free key at: https://www.themoviedb.org/settings/api')
        return

    # Load current data
    with open('movies_enriched.json') as f:
        movies = json.load(f)

    # Find Mom entry
    mom = None
    for movie in movies:
        if movie.get('title') == 'Mom':
            mom = movie
            break

    if not mom:
        print('❌ Mom not found in data')
        return

    print('Searching TMDb for: Mom 2017')
    print()

    # Search TMDb for Mom 2017
    url = 'https://api.themoviedb.org/3/search/movie'
    params = {
        'api_key': tmdb_api_key,
        'query': 'Mom',
        'year': 2017,
        'language': 'en-US'
    }

    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    if 'results' in data and len(data['results']) > 0:
        print(f'Found {len(data["results"])} results')
        print()

        # Show all results to pick the right one
        for i, result in enumerate(data['results'], 1):
            title = result.get('title', 'N/A')
            year = result.get('release_date', 'N/A')[:4] if result.get('release_date') else 'N/A'
            tmdb_id = result.get('id')
            poster_path = result.get('poster_path')
            overview = result.get('overview', '')[:80]

            print(f'{i}. TMDb ID: {tmdb_id}')
            print(f'   Title: {title} ({year})')
            print(f'   Poster: {poster_path}')
            print(f'   Overview: {overview}...')
            print()

            # Check if this is the Hindi film (usually has specific keywords)
            if poster_path and ('revenge' in overview.lower() or 'daughter' in overview.lower() or 'devki' in overview.lower()):
                # This is likely the Hindi film
                mom['tmdb_id'] = tmdb_id
                mom['tmdb_media_type'] = 'movie'
                mom['poster_url_medium'] = f'https://image.tmdb.org/t/p/w500{poster_path}'
                mom['poster_url_large'] = f'https://image.tmdb.org/t/p/original{poster_path}'

                print(f'✅ Selected result {i} as correct movie')
                print(f'   Poster URL: {mom["poster_url_medium"]}')
                print()

                # Test if poster is accessible
                test_response = requests.head(mom['poster_url_medium'], timeout=5)
                if test_response.status_code == 200:
                    print('✅ Poster URL is accessible')
                else:
                    print(f'⚠️  Poster returned HTTP {test_response.status_code}')

                break

        # Save updated data
        with open('movies_enriched.json', 'w', encoding='utf-8') as f:
            json.dump(movies, f, indent=2, ensure_ascii=False)

        print()
        print('💾 Updated movies_enriched.json')
    else:
        print('❌ No results found')

if __name__ == '__main__':
    main()
