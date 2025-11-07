#!/usr/bin/env python3
"""
Quick script to re-fetch YouTube trailers with improved search
Uses existing movies_enriched.json and updates only YouTube data
"""

import json
import re
import os
import time
import requests
from imdb import Cinemagoer

def extract_language_from_url(url):
    """Extract language from Binged URL for better search accuracy"""
    if not url:
        return None

    language_patterns = {
        'hindi': 'Hindi',
        'tamil': 'Tamil',
        'telugu': 'Telugu',
        'malayalam': 'Malayalam',
        'kannada': 'Kannada',
        'bengali': 'Bengali',
        'marathi': 'Marathi',
        'punjabi': 'Punjabi',
        'gujarati': 'Gujarati',
        'korean': 'Korean',
        'japanese': 'Japanese',
        'mandarin': 'Chinese',
        'spanish': 'Spanish',
        'french': 'French',
        'german': 'German',
        'italian': 'Italian',
        'portuguese': 'Portuguese',
        'russian': 'Russian',
        'indonesian': 'Indonesian',
        'tagalog': 'Filipino'
    }

    url_lower = url.lower()
    for pattern, language in language_patterns.items():
        if f'-{pattern}-' in url_lower or f'/{pattern}-' in url_lower:
            return language

    return None

def main():
    # Load existing data
    with open('movies_enriched.json') as f:
        movies = json.load(f)

    print(f"Loaded {len(movies)} movies")
    print("Re-fetching YouTube trailers with improved search...")
    print()

    ia = Cinemagoer()
    youtube_api_key = os.environ.get('YOUTUBE_API_KEY')

    updated_count = 0

    for i, movie in enumerate(movies, 1):
        title = movie.get('title', '')
        year = movie.get('imdb_year', '')
        url = movie.get('url', '')
        imdb_id = movie.get('imdb_id', '')

        # Fetch year from IMDb if missing
        if imdb_id and not year:
            try:
                movie_id = imdb_id.replace('tt', '')
                movie_info = ia.get_movie(movie_id)
                if 'year' in movie_info:
                    year = str(movie_info['year'])
                    movie['imdb_year'] = year
            except:
                pass

        # Extract language
        language = extract_language_from_url(url)

        # Build search query
        search_parts = [title]
        if language:
            search_parts.append(language)
        if year:
            search_parts.append(year)
        search_parts.append('official trailer')

        search_query = ' '.join(search_parts)

        print(f"[{i}/{len(movies)}] {title[:30]:30} → {search_query[:50]:50} ", end='', flush=True)

        try:
            if youtube_api_key:
                # Use YouTube API
                api_url = "https://www.googleapis.com/youtube/v3/search"
                params = {
                    'part': 'snippet',
                    'q': search_query,
                    'type': 'video',
                    'maxResults': 1,
                    'key': youtube_api_key
                }
                response = requests.get(api_url, params=params, timeout=10)
                data = response.json()

                if 'items' in data and len(data['items']) > 0:
                    video_id = data['items'][0]['id']['videoId']
                    movie['youtube_id'] = video_id
                    movie['youtube_url'] = f"https://www.youtube.com/watch?v={video_id}"
                    updated_count += 1
                    print(f"✓ {video_id}")
                else:
                    print("✗ Not found")
            else:
                # Fallback: scrape YouTube
                search_url = f"https://www.youtube.com/results?search_query={requests.utils.quote(search_query)}"
                response = requests.get(search_url, timeout=10)
                match = re.search(r'"videoId":"([^"]+)"', response.text)

                if match:
                    video_id = match.group(1)
                    movie['youtube_id'] = video_id
                    movie['youtube_url'] = f"https://www.youtube.com/watch?v={video_id}"
                    updated_count += 1
                    print(f"✓ {video_id}")
                else:
                    print("✗ Not found")

            time.sleep(0.3)

        except Exception as e:
            print(f"✗ Error: {e}")

    # Save updated data
    with open('movies_enriched.json', 'w', encoding='utf-8') as f:
        json.dump(movies, f, indent=2, ensure_ascii=False)

    print()
    print(f"✅ Updated {updated_count}/{len(movies)} trailers")
    print(f"💾 Saved: movies_enriched.json")

if __name__ == '__main__':
    main()
