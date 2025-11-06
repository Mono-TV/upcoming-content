#!/usr/bin/env python3
"""
YouTube Trailer Enrichment Script
Adds YouTube trailer links to movie data using intelligent matching
"""

import json
import sys
import re
from typing import List, Dict, Optional
import requests
from urllib.parse import quote, urlencode
import time


def get_youtube_api_key():
    """
    Get YouTube API key from environment or config
    Returns None if not available
    """
    import os
    return os.environ.get('YOUTUBE_API_KEY')


def search_youtube_api(query: str, api_key: str, max_results: int = 5) -> List[Dict]:
    """
    Search YouTube using official API

    Args:
        query: Search query
        api_key: YouTube Data API key
        max_results: Maximum number of results to return

    Returns:
        List of video results with metadata
    """
    try:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'maxResults': max_results,
            'key': api_key,
            'order': 'relevance',
            'videoDefinition': 'high',
            'safeSearch': 'none'
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get('items', []):
            video_id = item['id'].get('videoId')
            snippet = item.get('snippet', {})

            if video_id:
                results.append({
                    'video_id': video_id,
                    'title': snippet.get('title', ''),
                    'description': snippet.get('description', ''),
                    'channel_title': snippet.get('channelTitle', ''),
                    'channel_id': snippet.get('channelId', ''),
                    'published_at': snippet.get('publishedAt', '')
                })

        return results

    except Exception as e:
        print(f"    ⚠️  API search failed: {e}", file=sys.stderr)
        return []


def search_youtube_scraping(query: str, max_results: int = 5) -> List[Dict]:
    """
    Search YouTube by scraping search results page (fallback method)

    Args:
        query: Search query
        max_results: Maximum number of results

    Returns:
        List of video results
    """
    try:
        search_url = f"https://www.youtube.com/results?search_query={quote(query)}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()

        # Extract video IDs from the page
        # YouTube embeds video data in JavaScript on the page
        video_pattern = r'"videoId":"([^"]+)"'
        title_pattern = r'"title":{"runs":\[{"text":"([^"]+)"}]'

        video_ids = re.findall(video_pattern, response.text)
        titles = re.findall(title_pattern, response.text)

        # Remove duplicates while preserving order
        seen = set()
        unique_videos = []

        for i, video_id in enumerate(video_ids[:max_results * 3]):  # Get extra to filter
            if video_id not in seen and len(unique_videos) < max_results:
                seen.add(video_id)
                title = titles[i] if i < len(titles) else ''
                unique_videos.append({
                    'video_id': video_id,
                    'title': title,
                    'description': '',
                    'channel_title': '',
                    'channel_id': ''
                })

        return unique_videos[:max_results]

    except Exception as e:
        print(f"    ⚠️  Scraping search failed: {e}", file=sys.stderr)
        return []


def is_official_trailer(video_data: Dict, movie_title: str, movie_year: str = None) -> tuple[bool, int]:
    """
    Determine if a video is likely an official trailer and score it

    Args:
        video_data: Video metadata
        movie_title: Movie title to match against
        movie_year: Movie release year

    Returns:
        Tuple of (is_valid, confidence_score)
    """
    title = video_data.get('title', '').lower()
    description = video_data.get('description', '').lower()
    channel = video_data.get('channel_title', '').lower()

    # Clean movie title for matching
    clean_movie_title = re.sub(r'[^\w\s]', '', movie_title.lower())

    score = 0

    # Check if title contains movie name
    if clean_movie_title in re.sub(r'[^\w\s]', '', title):
        score += 30
    else:
        # Partial match (for longer titles)
        movie_words = clean_movie_title.split()
        if len(movie_words) >= 2:
            matches = sum(1 for word in movie_words if len(word) > 3 and word in title)
            if matches >= len(movie_words) * 0.6:  # At least 60% of words match
                score += 20

    # Check for trailer keywords
    trailer_keywords = ['official trailer', 'trailer', 'official', 'teaser']
    for keyword in trailer_keywords:
        if keyword in title:
            score += 15
            break

    # Check for year match
    if movie_year and movie_year in title:
        score += 10

    # Prefer certain official channels/distributors
    official_indicators = [
        'official', 'studios', 'pictures', 'films', 'entertainment',
        'universal', 'paramount', 'warner', 'disney', 'sony', '20th century',
        'lionsgate', 'netflix', 'amazon', 'apple', 'hulu', 'hbo', 'max'
    ]
    for indicator in official_indicators:
        if indicator in channel:
            score += 20
            break

    # Penalize unwanted content
    unwanted_keywords = [
        'reaction', 'review', 'breakdown', 'explained', 'easter egg',
        'behind the scenes', 'making of', 'interview', 'clip', 'scene',
        'fan made', 'fanmade', 'fan-made', 'parody', 'spoof', 'honest trailer'
    ]
    for keyword in unwanted_keywords:
        if keyword in title or keyword in description:
            score -= 30
            break

    # Video must have minimum score to be valid
    is_valid = score >= 30

    return is_valid, score


def find_best_trailer(movie: Dict, use_api: bool = False, api_key: str = None) -> Optional[Dict]:
    """
    Find the best YouTube trailer for a movie

    Args:
        movie: Movie data dictionary
        use_api: Whether to use YouTube API
        api_key: YouTube API key (if using API)

    Returns:
        Dictionary with YouTube video data or None
    """
    title = movie.get('title', '')
    imdb_title = movie.get('imdb_title', title)
    year = movie.get('imdb_year', '')

    if not title:
        return None

    print(f"  Searching for trailer: '{title}' ({year})", file=sys.stderr)

    # Build search queries with different strategies
    search_queries = []

    # Strategy 1: Use IMDb title + year + official trailer
    if imdb_title and year:
        search_queries.append(f"{imdb_title} {year} official trailer")

    # Strategy 2: Use original title + year + official trailer
    if year:
        search_queries.append(f"{title} {year} official trailer")

    # Strategy 3: Use IMDb title + trailer (without year)
    if imdb_title:
        search_queries.append(f"{imdb_title} official trailer")

    # Strategy 4: Use original title + trailer
    search_queries.append(f"{title} official trailer")

    all_candidates = []

    # Try each search query
    for query in search_queries:
        if use_api and api_key:
            results = search_youtube_api(query, api_key, max_results=3)
        else:
            results = search_youtube_scraping(query, max_results=3)

        # Score each result
        for result in results:
            is_valid, score = is_official_trailer(result, title, year)
            if is_valid:
                result['confidence_score'] = score
                all_candidates.append(result)

        # If we found good matches, stop searching
        if len(all_candidates) >= 3:
            break

        # Small delay between queries
        time.sleep(0.5)

    if not all_candidates:
        print(f"    ❌ No suitable trailer found", file=sys.stderr)
        return None

    # Sort by confidence score and return best match
    all_candidates.sort(key=lambda x: x['confidence_score'], reverse=True)
    best_match = all_candidates[0]

    print(f"    ✅ Found: {best_match['title'][:60]}... (score: {best_match['confidence_score']})", file=sys.stderr)

    return {
        'youtube_id': best_match['video_id'],
        'youtube_url': f"https://www.youtube.com/watch?v={best_match['video_id']}",
        'youtube_title': best_match['title'],
        'youtube_channel': best_match.get('channel_title', ''),
        'confidence_score': best_match['confidence_score']
    }


def enrich_movies_with_youtube(input_file: str, output_file: str):
    """
    Read movies from JSON file and enrich with YouTube trailer links

    Args:
        input_file: Path to input JSON file
        output_file: Path to output JSON file
    """
    print("="*60, file=sys.stderr)
    print("YouTube Trailer Enrichment Script", file=sys.stderr)
    print("="*60, file=sys.stderr)

    # Check for API key
    api_key = get_youtube_api_key()
    use_api = api_key is not None

    if use_api:
        print("\n✅ Using YouTube Data API", file=sys.stderr)
    else:
        print("\n⚠️  No API key found, using web scraping method", file=sys.stderr)
        print("💡 Set YOUTUBE_API_KEY environment variable for better results", file=sys.stderr)

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

        print(f"\n[{idx}/{len(movies)}] Processing: {title}", file=sys.stderr)

        # Skip if already has YouTube ID
        if 'youtube_id' in movie and movie['youtube_id']:
            print(f"  ⏭️  Already has YouTube ID: {movie['youtube_id']}", file=sys.stderr)
            enriched_count += 1
            continue

        # Find trailer
        trailer_data = find_best_trailer(movie, use_api=use_api, api_key=api_key)

        if trailer_data:
            # Add YouTube data to movie
            movie.update(trailer_data)
            enriched_count += 1
        else:
            movie['youtube_id'] = None
            movie['youtube_url'] = None
            failed_count += 1

        # Rate limiting
        if idx < len(movies):
            time.sleep(1)  # 1 second delay between requests

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
    input_file = 'movies_with_imdb.json'
    output_file = 'movies_with_trailers.json'

    # Check if input file exists
    try:
        with open(input_file, 'r') as f:
            pass
    except FileNotFoundError:
        print(f"Error: {input_file} not found. Please run enrich_with_imdb.py first.", file=sys.stderr)
        sys.exit(1)

    enrich_movies_with_youtube(input_file, output_file)

    print(f"\n✅ Done! Enriched data saved to {output_file}", file=sys.stderr)
    print(f"💡 The original {input_file} is preserved unchanged.", file=sys.stderr)


if __name__ == "__main__":
    main()
