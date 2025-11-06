#!/usr/bin/env python3
"""
Poster Enrichment Script
Adds high-quality poster images from TMDb
"""

import json
import sys
import os
from typing import Optional, Dict
import requests
import time


def get_tmdb_api_key():
    """Get TMDb API key from environment"""
    return os.environ.get('TMDB_API_KEY')


def search_tmdb(title: str, year: str = None, imdb_id: str = None, api_key: str = None, max_retries: int = 3) -> Optional[Dict]:
    """
    Search for movie on TMDb and get poster

    Args:
        title: Movie title
        year: Release year
        imdb_id: IMDb ID for exact matching
        api_key: TMDb API key
        max_retries: Number of retries on timeout/failure

    Returns:
        Dictionary with poster URLs or None
    """
    if not api_key:
        return None

    base_url = "https://api.themoviedb.org/3"

    for attempt in range(max_retries):
        try:
            # Try finding by IMDb ID first (most accurate)
            if imdb_id:
                print(f"  Searching TMDb by IMDb ID: {imdb_id}", file=sys.stderr)
                url = f"{base_url}/find/{imdb_id}"
                params = {
                    'api_key': api_key,
                    'external_source': 'imdb_id'
                }

                response = requests.get(url, params=params, timeout=20)
                response.raise_for_status()
                data = response.json()

                # Check movie results
                movie_results = data.get('movie_results', [])
                if movie_results:
                    movie = movie_results[0]
                    return extract_poster_data(movie)

                # Check TV results
                tv_results = data.get('tv_results', [])
                if tv_results:
                    tv = tv_results[0]
                    return extract_poster_data(tv)

            # Fallback to search by title
            print(f"  Searching TMDb by title: '{title}'", file=sys.stderr)
            url = f"{base_url}/search/multi"
            params = {
                'api_key': api_key,
                'query': title,
                'include_adult': 'false'
            }

            if year:
                params['year'] = year

            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()

            results = data.get('results', [])
            if results:
                # Return first result
                return extract_poster_data(results[0])

            print(f"    ❌ No results found on TMDb", file=sys.stderr)
            return None

        except requests.Timeout:
            if attempt < max_retries - 1:
                print(f"    ⚠️  Timeout (attempt {attempt + 1}/{max_retries}), retrying...", file=sys.stderr)
                time.sleep(2)  # Wait before retry
                continue
            else:
                print(f"    ❌ Failed after {max_retries} timeout attempts", file=sys.stderr)
                return None

        except requests.RequestException as e:
            if attempt < max_retries - 1:
                print(f"    ⚠️  Network error (attempt {attempt + 1}/{max_retries}): {e}", file=sys.stderr)
                time.sleep(2)
                continue
            else:
                print(f"    ❌ Failed after {max_retries} attempts: {e}", file=sys.stderr)
                return None

        except Exception as e:
            print(f"    ❌ TMDb search failed: {e}", file=sys.stderr)
            return None

    return None


def extract_poster_data(item: Dict) -> Dict:
    """Extract poster URLs from TMDb item"""
    poster_path = item.get('poster_path')
    backdrop_path = item.get('backdrop_path')

    if not poster_path:
        return None

    # TMDb image base URL
    base_image_url = "https://image.tmdb.org/t/p"

    return {
        'poster_url_small': f"{base_image_url}/w185{poster_path}",
        'poster_url_medium': f"{base_image_url}/w342{poster_path}",
        'poster_url_large': f"{base_image_url}/w500{poster_path}",
        'poster_url_original': f"{base_image_url}/original{poster_path}",
        'backdrop_url': f"{base_image_url}/original{backdrop_path}" if backdrop_path else None,
        'tmdb_id': item.get('id'),
        'tmdb_title': item.get('title') or item.get('name'),
        'tmdb_media_type': item.get('media_type', 'movie')
    }


def enrich_movies_with_posters(input_file: str, output_file: str):
    """
    Read movies from JSON file and enrich with high-quality posters

    Args:
        input_file: Path to input JSON file
        output_file: Path to output JSON file
    """
    print("="*60, file=sys.stderr)
    print("Poster Enrichment Script (TMDb)", file=sys.stderr)
    print("="*60, file=sys.stderr)

    # Check for API key
    api_key = get_tmdb_api_key()

    if not api_key:
        print("\n❌ TMDb API key not found!", file=sys.stderr)
        print("💡 Get a free API key from: https://www.themoviedb.org/settings/api", file=sys.stderr)
        print("💡 Then set it: export TMDB_API_KEY='your_key_here'", file=sys.stderr)
        sys.exit(1)

    print("\n✅ Using TMDb API", file=sys.stderr)

    # Read existing movies
    print(f"\nReading movies from {input_file}...", file=sys.stderr)
    with open(input_file, 'r', encoding='utf-8') as f:
        movies = json.load(f)

    print(f"Found {len(movies)} movies to enrich\n", file=sys.stderr)

    # Process each movie
    enriched_count = 0
    failed_count = 0

    for idx, movie in enumerate(movies, 1):
        title = movie.get('title', '')
        imdb_id = movie.get('imdb_id')
        year = movie.get('imdb_year', '')

        print(f"\n[{idx}/{len(movies)}] Processing: {title}", file=sys.stderr)

        # Skip if already has high-quality poster
        if 'poster_url_large' in movie and movie['poster_url_large']:
            print(f"  ⏭️  Already has high-quality poster", file=sys.stderr)
            enriched_count += 1
            continue

        # Search TMDb
        poster_data = search_tmdb(title, year, imdb_id, api_key)

        if poster_data:
            # Add poster data to movie
            movie.update(poster_data)
            print(f"    ✅ Found poster: {poster_data.get('tmdb_title', title)}", file=sys.stderr)
            enriched_count += 1
        else:
            failed_count += 1

        # Rate limiting (TMDb allows 40 requests per 10 seconds)
        # Using 0.5s delay to be safer and avoid timeouts
        if idx < len(movies):
            time.sleep(0.5)

    # Save enriched data
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"Saving enriched data to {output_file}...", file=sys.stderr)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(movies, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}", file=sys.stderr)
    print("Summary:", file=sys.stderr)
    print(f"  Total movies: {len(movies)}", file=sys.stderr)
    print(f"  Successfully enriched: {enriched_count}", file=sys.stderr)
    print(f"  Failed to find: {failed_count}", file=sys.stderr)
    if len(movies) > 0:
        print(f"  Success rate: {enriched_count/len(movies)*100:.1f}%", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    # Also output to stdout for piping
    print(json.dumps(movies, indent=2, ensure_ascii=False))


def main():
    """Main function"""
    input_file = 'movies_with_trailers.json'
    output_file = 'movies_enriched.json'

    # Check if input file exists
    try:
        with open(input_file, 'r') as f:
            pass
    except FileNotFoundError:
        print(f"Error: {input_file} not found.", file=sys.stderr)
        print(f"Please run the complete pipeline first.", file=sys.stderr)
        sys.exit(1)

    enrich_movies_with_posters(input_file, output_file)

    print(f"\n✅ Done! Enriched data saved to {output_file}", file=sys.stderr)
    print(f"💡 Update index.html to use {output_file} instead of movies_with_trailers.json", file=sys.stderr)


if __name__ == "__main__":
    main()
