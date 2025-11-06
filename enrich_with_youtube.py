#!/usr/bin/env python3
"""
YouTube Trailer Enrichment Script - Optimized Async Version with Caching
Adds YouTube trailer links to movie data using intelligent matching
"""

import json
import sys
import re
from typing import List, Dict, Optional
import asyncio
import aiohttp
from urllib.parse import quote
import os
import hashlib


# Cache directory
CACHE_DIR = '.cache'
YOUTUBE_CACHE_FILE = os.path.join(CACHE_DIR, 'youtube_cache.json')


def load_cache() -> Dict:
    """Load YouTube cache from disk"""
    if os.path.exists(YOUTUBE_CACHE_FILE):
        try:
            with open(YOUTUBE_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_cache(cache: Dict):
    """Save YouTube cache to disk"""
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(YOUTUBE_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def get_cache_key(title: str, year: str = '') -> str:
    """Generate cache key from title and year"""
    key_str = f"{title.lower()}:{year or ''}"
    return hashlib.md5(key_str.encode()).hexdigest()


def get_youtube_api_key():
    """
    Get YouTube API key from environment or config
    Returns None if not available
    """
    import os
    return os.environ.get('YOUTUBE_API_KEY')


async def search_youtube_api(
    session: aiohttp.ClientSession,
    query: str,
    api_key: str,
    max_results: int = 5
) -> List[Dict]:
    """
    Search YouTube using official API

    Args:
        session: aiohttp session
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

        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status != 200:
                return []

            data = await response.json()

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


async def search_youtube_scraping(
    session: aiohttp.ClientSession,
    query: str,
    max_results: int = 5
) -> List[Dict]:
    """
    Search YouTube by scraping search results page (fallback method)

    Args:
        session: aiohttp session
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

        async with session.get(search_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status != 200:
                return []

            text = await response.text()

            # Extract video IDs from the page
            # YouTube embeds video data in JavaScript on the page
            video_pattern = r'"videoId":"([^"]+)"'
            title_pattern = r'"title":{"runs":\[{"text":"([^"]+)"}]'

            video_ids = re.findall(video_pattern, text)
            titles = re.findall(title_pattern, text)

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


async def find_best_trailer(
    session: aiohttp.ClientSession,
    movie: Dict,
    cache: Dict,
    use_api: bool = False,
    api_key: str = None
) -> Optional[Dict]:
    """
    Find the best YouTube trailer for a movie

    Args:
        session: aiohttp session
        movie: Movie data dictionary
        cache: Cache dictionary
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

    # Check cache first
    if cache is not None:
        cache_key = get_cache_key(title, year)
        if cache_key in cache:
            print(f"  📦 Using cached result", file=sys.stderr)
            return cache[cache_key]

    print(f"  Searching for trailer: '{title}' ({year})", file=sys.stderr)

    # Build search queries with different strategies (but only use first good match)
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

    # Try each search query, stop on first good match
    for query in search_queries:
        if use_api and api_key:
            results = await search_youtube_api(session, query, api_key, max_results=3)
        else:
            results = await search_youtube_scraping(session, query, max_results=3)

        # Score each result
        for result in results:
            is_valid, score = is_official_trailer(result, title, year)
            if is_valid:
                result['confidence_score'] = score
                all_candidates.append(result)

        # If we found good matches, stop searching
        if len(all_candidates) >= 2:
            break

        # Small delay between queries
        await asyncio.sleep(0.3)

    if not all_candidates:
        print(f"    ❌ No suitable trailer found", file=sys.stderr)
        result = None
        if cache is not None:
            cache[get_cache_key(title, year)] = result
        return result

    # Sort by confidence score and return best match
    all_candidates.sort(key=lambda x: x['confidence_score'], reverse=True)
    best_match = all_candidates[0]

    print(f"    ✅ Found: {best_match['title'][:60]}... (score: {best_match['confidence_score']})", file=sys.stderr)

    result = {
        'youtube_id': best_match['video_id'],
        'youtube_url': f"https://www.youtube.com/watch?v={best_match['video_id']}",
        'youtube_title': best_match['title'],
        'youtube_channel': best_match.get('channel_title', ''),
        'confidence_score': best_match['confidence_score']
    }

    # Cache the result
    if cache is not None:
        cache[get_cache_key(title, year)] = result

    return result


async def process_movie(
    session: aiohttp.ClientSession,
    movie: Dict,
    cache: Dict,
    semaphore: asyncio.Semaphore,
    use_api: bool = False,
    api_key: str = None
) -> Dict:
    """
    Process a single movie with rate limiting

    Args:
        session: aiohttp session
        movie: Movie dictionary
        cache: Cache dictionary
        semaphore: Semaphore for rate limiting
        use_api: Whether to use YouTube API
        api_key: YouTube API key

    Returns:
        Updated movie dictionary
    """
    async with semaphore:
        title = movie.get('title', '')

        # Skip if already has YouTube ID
        if 'youtube_id' in movie and movie['youtube_id']:
            print(f"  ⏭️  Already has YouTube ID: {movie['youtube_id']}", file=sys.stderr)
            return movie

        # Find trailer
        trailer_data = await find_best_trailer(session, movie, cache, use_api=use_api, api_key=api_key)

        if trailer_data:
            # Add YouTube data to movie
            movie.update(trailer_data)
        else:
            movie['youtube_id'] = None
            movie['youtube_url'] = None

        # Rate limiting
        await asyncio.sleep(0.3)

        return movie


async def enrich_movies_with_youtube(input_file: str, output_file: str, concurrency: int = 5):
    """
    Read movies from JSON file and enrich with YouTube trailer links

    Args:
        input_file: Path to input JSON file
        output_file: Path to output JSON file
        concurrency: Number of concurrent requests
    """
    print("="*60, file=sys.stderr)
    print("YouTube Trailer Enrichment Script (Optimized)", file=sys.stderr)
    print("="*60, file=sys.stderr)

    # Check for API key
    api_key = get_youtube_api_key()
    use_api = api_key is not None

    if use_api:
        print("\n✅ Using YouTube Data API", file=sys.stderr)
    else:
        print("\n⚠️  No API key found, using web scraping method", file=sys.stderr)
        print("💡 Set YOUTUBE_API_KEY environment variable for better results", file=sys.stderr)

    # Load cache
    cache = load_cache()
    print(f"\n📦 Loaded {len(cache)} cached entries", file=sys.stderr)

    # Read existing movies
    print(f"\nReading movies from {input_file}...", file=sys.stderr)
    with open(input_file, 'r', encoding='utf-8') as f:
        movies = json.load(f)

    print(f"Found {len(movies)} movies to enrich\n", file=sys.stderr)

    # Process movies concurrently with rate limiting
    enriched_count = 0
    failed_count = 0

    # Create semaphore for rate limiting
    semaphore = asyncio.Semaphore(concurrency)

    async with aiohttp.ClientSession() as session:
        tasks = []
        for idx, movie in enumerate(movies, 1):
            title = movie.get('title', '')
            print(f"\n[{idx}/{len(movies)}] Processing: {title}", file=sys.stderr)
            task = process_movie(session, movie, cache, semaphore, use_api=use_api, api_key=api_key)
            tasks.append(task)

        # Process all movies concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Update movies with results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Error processing movie {i+1}: {result}", file=sys.stderr)
                failed_count += 1
            else:
                movies[i] = result
                if result.get('youtube_id'):
                    enriched_count += 1
                else:
                    failed_count += 1

    # Save cache
    save_cache(cache)
    print(f"\n💾 Saved {len(cache)} entries to cache", file=sys.stderr)

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

    asyncio.run(enrich_movies_with_youtube(input_file, output_file, concurrency=5))

    print(f"\n✅ Done! Enriched data saved to {output_file}", file=sys.stderr)
    print(f"💡 The original {input_file} is preserved unchanged.", file=sys.stderr)


if __name__ == "__main__":
    main()
