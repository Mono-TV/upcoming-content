#!/usr/bin/env python3
"""
TMDB Upcoming Content Scraper
Fetches upcoming movies and TV shows from TMDB API with streaming platform information
Uses TMDB's discover endpoints and watch providers for accurate, comprehensive data
"""

import json
import os
import sys
import argparse
import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Check required packages
try:
    import requests
except ImportError:
    print("❌ Missing required package: requests")
    print("\n💡 Install: pip3 install requests")
    sys.exit(1)


class TMDBUpcomingScraper:
    """Scraper for upcoming movies and TV shows using TMDB API"""

    # Streaming platform IDs in India
    INDIAN_PLATFORMS = {
        8: 'Netflix',
        9: 'Amazon Prime Video',
        122: 'Jio Hotstar',  # Disney+ Hotstar
        232: 'Zee5',
        237: 'Sony LIV',
        309: 'Sun NXT',
        350: 'Apple TV+',
        532: 'Aha Video',
        # Add more as needed
    }

    def __init__(self, days_ahead=60, include_theatrical=True, include_streaming=True):
        """
        Initialize scraper

        Args:
            days_ahead: How many days ahead to look for releases
            include_theatrical: Include theatrical releases
            include_streaming: Include streaming releases
        """
        self.tmdb_api_key = os.environ.get('TMDB_API_KEY')
        if not self.tmdb_api_key:
            print("\n" + "="*70)
            print("❌ TMDB API KEY REQUIRED")
            print("="*70)
            print("\nSet environment variable:")
            print("   export TMDB_API_KEY='your_key_here'")
            print("\n" + "="*70 + "\n")
            sys.exit(1)

        self.days_ahead = days_ahead
        self.include_theatrical = include_theatrical
        self.include_streaming = include_streaming

        # Calculate date range
        self.today = datetime.now().date()
        self.end_date = self.today + timedelta(days=days_ahead)

        self.movies = []
        self.tv_shows = []

    def _fetch_with_retry(self, url, params, max_retries=3):
        """Fetch URL with retry logic"""
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                return response.json()
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                if attempt < max_retries - 1:
                    time.sleep((attempt + 1) * 2)
                    continue
                else:
                    raise
            except Exception:
                raise

    def _get_watch_providers(self, item_id: int, media_type: str) -> List[str]:
        """Get streaming platforms for a movie/TV show in India"""
        try:
            url = f"https://api.themoviedb.org/3/{media_type}/{item_id}/watch/providers"
            params = {'api_key': self.tmdb_api_key}

            data = self._fetch_with_retry(url, params)

            # Get India-specific providers
            india_providers = data.get('results', {}).get('IN', {})

            platforms = []

            # Check flatrate (subscription streaming)
            for provider in india_providers.get('flatrate', []):
                provider_id = provider.get('provider_id')
                if provider_id in self.INDIAN_PLATFORMS:
                    platform_name = self.INDIAN_PLATFORMS[provider_id]
                    if platform_name not in platforms:
                        platforms.append(platform_name)

            return platforms

        except Exception as e:
            return []

    def discover_movies(self):
        """Discover upcoming movies using TMDB discover endpoint"""

        print("\n" + "="*70)
        print("DISCOVERING UPCOMING MOVIES FROM TMDB")
        print("="*70)
        print(f"Date range: {self.today} to {self.end_date}")
        print(f"Region: India (IN)")
        print("="*70 + "\n")

        all_movies = []
        page = 1
        total_pages = 1

        while page <= total_pages and page <= 10:  # Limit to 10 pages max
            try:
                url = "https://api.themoviedb.org/3/discover/movie"
                params = {
                    'api_key': self.tmdb_api_key,
                    'region': 'IN',
                    'language': 'en-US',
                    'release_date.gte': str(self.today),
                    'release_date.lte': str(self.end_date),
                    'sort_by': 'release_date.asc',
                    'page': page
                }

                print(f"📄 Fetching page {page}...", end=' ', flush=True)
                data = self._fetch_with_retry(url, params)

                total_pages = data.get('total_pages', 1)
                results = data.get('results', [])

                print(f"Found {len(results)} movies")

                all_movies.extend(results)
                page += 1
                time.sleep(0.25)  # Rate limiting

            except Exception as e:
                print(f"\n⚠️  Error fetching page {page}: {e}")
                break

        print(f"\n✅ Discovered {len(all_movies)} total movies")
        return all_movies

    def discover_tv_shows(self):
        """Discover upcoming TV shows using TMDB discover endpoint"""

        print("\n" + "="*70)
        print("DISCOVERING UPCOMING TV SHOWS FROM TMDB")
        print("="*70)
        print(f"Date range: {self.today} to {self.end_date}")
        print("="*70 + "\n")

        all_shows = []
        page = 1
        total_pages = 1

        while page <= total_pages and page <= 10:  # Limit to 10 pages max
            try:
                url = "https://api.themoviedb.org/3/discover/tv"
                params = {
                    'api_key': self.tmdb_api_key,
                    'language': 'en-US',
                    'air_date.gte': str(self.today),
                    'air_date.lte': str(self.end_date),
                    'sort_by': 'first_air_date.asc',
                    'page': page
                }

                print(f"📄 Fetching page {page}...", end=' ', flush=True)
                data = self._fetch_with_retry(url, params)

                total_pages = data.get('total_pages', 1)
                results = data.get('results', [])

                print(f"Found {len(results)} shows")

                all_shows.extend(results)
                page += 1
                time.sleep(0.25)  # Rate limiting

            except Exception as e:
                print(f"\n⚠️  Error fetching page {page}: {e}")
                break

        print(f"\n✅ Discovered {len(all_shows)} total TV shows")
        return all_shows

    def enrich_with_platforms(self, items, media_type):
        """Enrich items with streaming platform information"""

        print(f"\n" + "="*70)
        print(f"FETCHING STREAMING PLATFORMS FOR {media_type.upper()}")
        print("="*70 + "\n")

        enriched_items = []

        for i, item in enumerate(items, 1):
            item_id = item['id']
            title = item.get('title') or item.get('name', 'Unknown')

            print(f"[{i}/{len(items)}] {title[:50]}... ", end='', flush=True)

            # Get watch providers
            platforms = self._get_watch_providers(item_id, media_type)

            # Only include if has streaming platform OR if include_theatrical is True
            if platforms or self.include_theatrical:
                # Build structured data
                enriched_item = {
                    'title': title,
                    'tmdb_id': item_id,
                    'tmdb_media_type': media_type,
                    'release_date': item.get('release_date') or item.get('first_air_date'),
                    'overview': item.get('overview', ''),
                    'poster_path': item.get('poster_path'),
                    'backdrop_path': item.get('backdrop_path'),
                    'original_language': item.get('original_language'),
                    'original_title': item.get('original_title') or item.get('original_name'),
                    'tmdb_rating': item.get('vote_average'),
                    'tmdb_vote_count': item.get('vote_count'),
                    'popularity': item.get('popularity'),
                    'platforms': platforms if platforms else []
                }

                # Add posters
                if item.get('poster_path'):
                    poster_path = item['poster_path']
                    enriched_item['posters'] = {
                        'thumbnail': f"https://image.tmdb.org/t/p/w92{poster_path}",
                        'small': f"https://image.tmdb.org/t/p/w185{poster_path}",
                        'medium': f"https://image.tmdb.org/t/p/w342{poster_path}",
                        'large': f"https://image.tmdb.org/t/p/w500{poster_path}",
                        'xlarge': f"https://image.tmdb.org/t/p/w780{poster_path}",
                        'original': f"https://image.tmdb.org/t/p/original{poster_path}"
                    }
                    enriched_item['poster_url_medium'] = enriched_item['posters']['medium']
                    enriched_item['poster_url_large'] = enriched_item['posters']['large']

                # Add backdrops
                if item.get('backdrop_path'):
                    backdrop_path = item['backdrop_path']
                    enriched_item['backdrops'] = {
                        'small': f"https://image.tmdb.org/t/p/w300{backdrop_path}",
                        'medium': f"https://image.tmdb.org/t/p/w780{backdrop_path}",
                        'large': f"https://image.tmdb.org/t/p/w1280{backdrop_path}",
                        'original': f"https://image.tmdb.org/t/p/original{backdrop_path}"
                    }
                    enriched_item['backdrop_url'] = enriched_item['backdrops']['original']

                enriched_items.append(enriched_item)

                if platforms:
                    print(f"✓ {len(platforms)} platform(s): {', '.join(platforms[:2])}")
                else:
                    print(f"⊙ Theatrical only")
            else:
                print(f"✗ No streaming platforms")

            time.sleep(0.25)  # Rate limiting

        print(f"\n✅ Enriched {len(enriched_items)} items with platform info")
        return enriched_items

    def save_json(self, data, filename):
        """Save data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved: {filename}")

    def run(self):
        """Run the scraper"""

        start_time = time.time()

        print("\n" + "="*70)
        print("TMDB UPCOMING CONTENT SCRAPER")
        print("="*70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Looking ahead: {self.days_ahead} days")
        print("="*70)

        # Discover movies
        movies = self.discover_movies()

        # Discover TV shows
        tv_shows = self.discover_tv_shows()

        # Enrich with platforms
        if movies:
            self.movies = self.enrich_with_platforms(movies, 'movie')
            self.save_json(self.movies, 'tmdb_upcoming_movies.json')

        if tv_shows:
            self.tv_shows = self.enrich_with_platforms(tv_shows, 'tv')
            self.save_json(self.tv_shows, 'tmdb_upcoming_tv.json')

        # Combined file
        all_content = self.movies + self.tv_shows
        if all_content:
            self.save_json(all_content, 'tmdb_upcoming_all.json')

        # Summary
        elapsed = time.time() - start_time

        # Platform distribution
        platform_counts = {}
        for item in all_content:
            for platform in item.get('platforms', []):
                platform_counts[platform] = platform_counts.get(platform, 0) + 1

        print("\n" + "="*70)
        print("✅ SCRAPING COMPLETE!")
        print("="*70)
        print(f"\n📊 Summary:")
        print(f"   • Movies discovered: {len(self.movies)}")
        print(f"   • TV shows discovered: {len(self.tv_shows)}")
        print(f"   • Total content: {len(all_content)}")

        if platform_counts:
            print(f"\n📺 Platform Distribution:")
            for platform, count in sorted(platform_counts.items(), key=lambda x: -x[1]):
                print(f"   • {platform}: {count} items")

        print(f"\n⏱️  Time elapsed: {elapsed:.1f} seconds")
        print(f"\n📁 Files created:")
        print(f"   • tmdb_upcoming_movies.json")
        print(f"   • tmdb_upcoming_tv.json")
        print(f"   • tmdb_upcoming_all.json")
        print("\n" + "="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Scrape upcoming movies and TV shows from TMDB API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scrape_tmdb_upcoming.py                    # Next 60 days (default)
  python3 scrape_tmdb_upcoming.py --days 30         # Next 30 days
  python3 scrape_tmdb_upcoming.py --days 90         # Next 90 days
  python3 scrape_tmdb_upcoming.py --streaming-only  # Only streaming releases
        """
    )

    parser.add_argument(
        '--days',
        type=int,
        default=60,
        help='Number of days to look ahead (default: 60)'
    )

    parser.add_argument(
        '--streaming-only',
        action='store_true',
        help='Only include content with streaming platforms (exclude theatrical-only)'
    )

    args = parser.parse_args()

    scraper = TMDBUpcomingScraper(
        days_ahead=args.days,
        include_theatrical=not args.streaming_only,
        include_streaming=True
    )

    try:
        scraper.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
