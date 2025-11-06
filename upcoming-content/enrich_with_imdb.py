#!/usr/bin/env python3
"""
IMDb ID Enrichment Script - Web Scraping Version
Reads movies.json and adds IMDb IDs by scraping IMDb search
"""

import json
import sys
import re
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import quote


def clean_title(title: str) -> str:
    """
    Clean movie title for better matching

    Args:
        title: Original movie title

    Returns:
        Cleaned title
    """
    # Remove common suffixes and extra info
    title = re.sub(r'\s*\(.*?\)\s*', '', title)  # Remove (2024), (Hindi), etc.
    title = re.sub(r'\s*Season\s+\d+.*', '', title, flags=re.IGNORECASE)  # Remove Season info
    title = re.sub(r'\s*S\d+.*', '', title, flags=re.IGNORECASE)  # Remove S01, S02 etc.
    title = title.strip()
    return title


def search_imdb_web(title: str, year: Optional[int] = None, max_retries: int = 3) -> Optional[Dict]:
    """
    Search for a movie on IMDb using web scraping

    Args:
        title: Movie title to search for
        year: Optional release year for better matching
        max_retries: Number of retries on failure

    Returns:
        Dictionary with imdb_id and other info, or None if not found
    """
    cleaned_title = clean_title(title)

    for attempt in range(max_retries):
        try:
            print(f"  Searching IMDb for: '{cleaned_title}'", file=sys.stderr)

            # Construct search URL
            search_query = quote(cleaned_title)
            search_url = f"https://www.imdb.com/find/?q={search_query}&s=tt&ttype=ft,tv"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }

            # Make request
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for exact results section first
            exact_results = soup.find('section', {'data-testid': 'find-results-section-title'})

            if not exact_results:
                # Try alternative selectors
                exact_results = soup.find('ul', class_='ipc-metadata-list')

            if not exact_results:
                print(f"    ❌ No results found", file=sys.stderr)
                return None

            # Find the first result
            first_result = exact_results.find('li', class_='ipc-metadata-list-summary-item')

            if not first_result:
                # Try finding by different class
                first_result = exact_results.find('li')

            if not first_result:
                print(f"    ❌ No results in section", file=sys.stderr)
                return None

            # Extract IMDb ID from link
            link = first_result.find('a', href=True)
            if not link:
                print(f"    ❌ No link found", file=sys.stderr)
                return None

            href = link['href']
            imdb_match = re.search(r'/title/(tt\d+)', href)

            if not imdb_match:
                print(f"    ❌ Could not extract IMDb ID from link", file=sys.stderr)
                return None

            imdb_id = imdb_match.group(1)

            # Extract title - now in h3 tag with class ipc-title__text
            title_elem = first_result.find('h3', class_='ipc-title__text')
            imdb_title = title_elem.get_text(strip=True) if title_elem else ''

            # Look for year - now in metadata section
            metadata_div = first_result.find('div', class_='cli-title-metadata')
            imdb_year = ''
            if metadata_div:
                # Year is typically the first metadata item
                metadata_items = metadata_div.find_all('span', class_='cli-title-metadata-item')
                if metadata_items:
                    # Check first few items for a year (YYYY format)
                    for item in metadata_items[:3]:
                        item_text = item.get_text(strip=True)
                        year_match = re.search(r'^\d{4}$', item_text)
                        if year_match:
                            imdb_year = year_match.group(0)
                            break

            print(f"    ✅ Found: {imdb_title} ({imdb_year}) [{imdb_id}]", file=sys.stderr)

            return {
                'imdb_id': imdb_id,
                'imdb_title': imdb_title,
                'imdb_year': imdb_year,
                'imdb_url': f'https://www.imdb.com/title/{imdb_id}/'
            }

        except requests.RequestException as e:
            if attempt < max_retries - 1:
                print(f"    ⚠️  Network error (attempt {attempt + 1}/{max_retries}): {e}", file=sys.stderr)
                time.sleep(2)
            else:
                print(f"    ❌ Failed after {max_retries} attempts: {e}", file=sys.stderr)
                return None
        except Exception as e:
            print(f"    ❌ Error: {e}", file=sys.stderr)
            return None

    return None


def extract_year_from_date(release_date: str) -> Optional[int]:
    """
    Extract year from release date string

    Args:
        release_date: Date string like "05 Nov 2025"

    Returns:
        Year as integer, or None if not found
    """
    match = re.search(r'\d{4}', release_date)
    if match:
        return int(match.group(0))
    return None


def enrich_movies_with_imdb(input_file: str, output_file: str):
    """
    Read movies from JSON file and enrich with IMDb IDs

    Args:
        input_file: Path to input JSON file
        output_file: Path to output JSON file
    """
    print("="*60, file=sys.stderr)
    print("IMDb ID Enrichment Script (Web Scraping)", file=sys.stderr)
    print("="*60, file=sys.stderr)

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
        release_date = movie.get('release_date', '')
        year = extract_year_from_date(release_date) if release_date else None

        print(f"\n[{idx}/{len(movies)}] Processing: {title}", file=sys.stderr)

        # Skip if already has IMDb ID
        if 'imdb_id' in movie and movie['imdb_id']:
            print(f"  ⏭️  Already has IMDb ID: {movie['imdb_id']}", file=sys.stderr)
            enriched_count += 1
            continue

        # Search for IMDb ID
        imdb_data = search_imdb_web(title, year)

        if imdb_data:
            # Add IMDb data to movie
            movie['imdb_id'] = imdb_data['imdb_id']
            if 'imdb_title' in imdb_data:
                movie['imdb_title'] = imdb_data['imdb_title']
            if 'imdb_year' in imdb_data:
                movie['imdb_year'] = imdb_data['imdb_year']
            if 'imdb_url' in imdb_data:
                movie['imdb_url'] = imdb_data['imdb_url']
            enriched_count += 1
        else:
            movie['imdb_id'] = None
            failed_count += 1

        # Delay to be respectful to IMDb servers
        if idx < len(movies):
            time.sleep(1.5)  # 1.5 second delay between requests

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
    input_file = 'movies.json'
    output_file = 'movies_with_imdb.json'

    # Check if input file exists
    try:
        with open(input_file, 'r') as f:
            pass
    except FileNotFoundError:
        print(f"Error: {input_file} not found. Please run scrape_movies.py first.", file=sys.stderr)
        sys.exit(1)

    enrich_movies_with_imdb(input_file, output_file)

    print(f"\n✅ Done! Enriched data saved to {output_file}", file=sys.stderr)
    print(f"💡 The original {input_file} is preserved unchanged.", file=sys.stderr)


if __name__ == "__main__":
    main()
