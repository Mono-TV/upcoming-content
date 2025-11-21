#!/usr/bin/env python3
"""
TMDB-Based Content Updater
Comprehensive scraper using TMDB API for discovery and enrichment
Replaces Binged.com scraping with official TMDB API

Usage:
    python3 update_content_tmdb.py [--days N] [--test]
"""

import json
import os
import sys
import time
import argparse
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Check required packages
try:
    import requests
except ImportError:
    print("❌ Missing required package: requests")
    print("\n💡 Install: pip3 install requests")
    sys.exit(1)


class TMDBContentUpdater:
    """Complete content updater using TMDB API for discovery and enrichment"""

    # Indian streaming platforms
    INDIAN_PLATFORMS = {
        8: 'Netflix',
        9: 'Amazon Prime Video',
        122: 'Jio Hotstar',
        232: 'Zee5',
        237: 'Sony LIV',
        309: 'Sun NXT',
        350: 'Apple TV+',
        532: 'Aha Video',
    }

    def __init__(self, days_ahead=60, test_mode=False):
        self.days_ahead = days_ahead
        self.test_mode = test_mode
        self.content = []

        # TMDB API
        self.tmdb_api_key = os.environ.get('TMDB_API_KEY')
        if not self.tmdb_api_key:
            print("\n" + "="*70)
            print("❌ TMDB API KEY REQUIRED")
            print("="*70)
            print("\nSet environment variable:")
            print("   export TMDB_API_KEY='your_key_here'")
            print("\n" + "="*70 + "\n")
            sys.exit(1)

        # Date range
        self.today = datetime.now().date()
        self.end_date = self.today + timedelta(days=days_ahead)

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

    def discover_content(self, media_type='movie'):
        """Discover upcoming content from TMDB"""

        content_items = []
        page = 1
        max_pages = 1 if self.test_mode else 10

        date_field = 'release_date' if media_type == 'movie' else 'air_date'

        while page <= max_pages:
            try:
                url = f"https://api.themoviedb.org/3/discover/{media_type}"
                params = {
                    'api_key': self.tmdb_api_key,
                    'language': 'en-US',
                    f'{date_field}.gte': str(self.today),
                    f'{date_field}.lte': str(self.end_date),
                    'sort_by': f'{"release_date" if media_type == "movie" else "first_air_date"}.asc',
                    'page': page
                }

                if media_type == 'movie':
                    params['region'] = 'IN'

                data = self._fetch_with_retry(url, params)

                results = data.get('results', [])
                if not results:
                    break

                content_items.extend(results)

                total_pages = min(data.get('total_pages', 1), max_pages)
                if page >= total_pages:
                    break

                page += 1
                time.sleep(0.25)

            except Exception as e:
                print(f"    Error on page {page}: {e}")
                break

        return content_items

    def get_watch_providers(self, item_id: int, media_type: str) -> List[str]:
        """Get streaming platforms for India"""
        try:
            url = f"https://api.themoviedb.org/3/{media_type}/{item_id}/watch/providers"
            params = {'api_key': self.tmdb_api_key}

            data = self._fetch_with_retry(url, params)
            india_providers = data.get('results', {}).get('IN', {})

            platforms = []
            for provider in india_providers.get('flatrate', []):
                provider_id = provider.get('provider_id')
                if provider_id in self.INDIAN_PLATFORMS:
                    platform_name = self.INDIAN_PLATFORMS[provider_id]
                    if platform_name not in platforms:
                        platforms.append(platform_name)

            return platforms

        except:
            return []

    def get_full_details(self, item_id: int, media_type: str) -> Optional[Dict]:
        """Get full details for a movie/show"""
        try:
            url = f"https://api.themoviedb.org/3/{media_type}/{item_id}"
            params = {
                'api_key': self.tmdb_api_key,
                'language': 'en-US'
            }
            return self._fetch_with_retry(url, params)
        except:
            return None

    def get_external_ids(self, item_id: int, media_type: str) -> Optional[Dict]:
        """Get external IDs (IMDb)"""
        try:
            url = f"https://api.themoviedb.org/3/{media_type}/{item_id}/external_ids"
            params = {'api_key': self.tmdb_api_key}
            return self._fetch_with_retry(url, params)
        except:
            return None

    def get_images(self, item_id: int, media_type: str, image_type: str) -> List[Dict]:
        """Get images with language filtering"""
        try:
            url = f"https://api.themoviedb.org/3/{media_type}/{item_id}/images"
            params = {'api_key': self.tmdb_api_key}

            data = self._fetch_with_retry(url, params)
            images = data.get(image_type, [])

            # Filter for English or Indian languages
            preferred_langs = ['en', 'hi', 'ta', 'te', 'ml', 'kn', 'bn', 'mr', None]
            preferred_images = [img for img in images if img.get('iso_639_1') in preferred_langs]

            if not preferred_images:
                preferred_images = images

            # Sort by quality
            preferred_images.sort(key=lambda x: x.get('vote_average', 0), reverse=True)

            return preferred_images

        except:
            return []

    def get_credits(self, item_id: int, media_type: str) -> Optional[Dict]:
        """Get cast and crew"""
        try:
            url = f"https://api.themoviedb.org/3/{media_type}/{item_id}/credits"
            params = {'api_key': self.tmdb_api_key}
            return self._fetch_with_retry(url, params)
        except:
            return None

    def get_videos(self, item_id: int, media_type: str) -> List[Dict]:
        """Get videos (trailers)"""
        try:
            url = f"https://api.themoviedb.org/3/{media_type}/{item_id}/videos"
            params = {
                'api_key': self.tmdb_api_key,
                'language': 'en-US'
            }
            data = self._fetch_with_retry(url, params)
            return data.get('results', [])
        except:
            return []

    def enrich_item(self, item: Dict, media_type: str) -> Dict:
        """Fully enrich a single item with all metadata"""

        item_id = item['id']
        title = item.get('title') or item.get('name', 'Unknown')

        enriched = {
            'title': title,
            'tmdb_id': item_id,
            'tmdb_media_type': media_type,
            'release_date': item.get('release_date') or item.get('first_air_date'),
            'overview': item.get('overview', ''),
            'original_title': item.get('original_title') or item.get('original_name'),
            'original_language': item.get('original_language'),
            'tmdb_rating': item.get('vote_average'),
            'tmdb_vote_count': item.get('vote_count'),
            'popularity': item.get('popularity'),
        }

        # Get streaming platforms
        platforms = self.get_watch_providers(item_id, media_type)
        enriched['platforms'] = platforms

        # Get full details
        details = self.get_full_details(item_id, media_type)
        if details:
            enriched['description'] = details.get('overview', '')

            # Genres
            genres = details.get('genres', [])
            enriched['genres'] = [g['name'] for g in genres]

            # Runtime
            if media_type == 'movie':
                enriched['runtime'] = details.get('runtime')
            else:
                enriched['episode_runtime'] = details.get('episode_run_time', [])
                enriched['number_of_seasons'] = details.get('number_of_seasons')
                enriched['number_of_episodes'] = details.get('number_of_episodes')

            enriched['tmdb_release_date'] = details.get('release_date') or details.get('first_air_date')
            enriched['status'] = details.get('status')

        # External IDs
        external_ids = self.get_external_ids(item_id, media_type)
        if external_ids:
            imdb_id = external_ids.get('imdb_id')
            if imdb_id:
                enriched['imdb_id'] = imdb_id

        # Posters (with language filtering)
        posters = self.get_images(item_id, media_type, 'posters')
        if posters:
            poster_path = posters[0]['file_path']
            enriched['posters'] = {
                'thumbnail': f"https://image.tmdb.org/t/p/w92{poster_path}",
                'small': f"https://image.tmdb.org/t/p/w185{poster_path}",
                'medium': f"https://image.tmdb.org/t/p/w342{poster_path}",
                'large': f"https://image.tmdb.org/t/p/w500{poster_path}",
                'xlarge': f"https://image.tmdb.org/t/p/w780{poster_path}",
                'original': f"https://image.tmdb.org/t/p/original{poster_path}"
            }
            enriched['poster_url_medium'] = enriched['posters']['medium']
            enriched['poster_url_large'] = enriched['posters']['large']
            enriched['poster_language'] = posters[0].get('iso_639_1') or 'none'

            # Store all posters
            enriched['all_posters'] = [
                {
                    'thumbnail': f"https://image.tmdb.org/t/p/w92{p['file_path']}",
                    'small': f"https://image.tmdb.org/t/p/w185{p['file_path']}",
                    'medium': f"https://image.tmdb.org/t/p/w342{p['file_path']}",
                    'large': f"https://image.tmdb.org/t/p/w500{p['file_path']}",
                    'xlarge': f"https://image.tmdb.org/t/p/w780{p['file_path']}",
                    'original': f"https://image.tmdb.org/t/p/original{p['file_path']}",
                    'language': p.get('iso_639_1')
                }
                for p in posters[:5]
            ]

        # Backdrops
        backdrops = self.get_images(item_id, media_type, 'backdrops')
        if backdrops:
            backdrop_path = backdrops[0]['file_path']
            enriched['backdrops'] = {
                'small': f"https://image.tmdb.org/t/p/w300{backdrop_path}",
                'medium': f"https://image.tmdb.org/t/p/w780{backdrop_path}",
                'large': f"https://image.tmdb.org/t/p/w1280{backdrop_path}",
                'original': f"https://image.tmdb.org/t/p/original{backdrop_path}"
            }
            enriched['backdrop_url'] = enriched['backdrops']['original']

            enriched['all_backdrops'] = [
                {
                    'small': f"https://image.tmdb.org/t/p/w300{b['file_path']}",
                    'medium': f"https://image.tmdb.org/t/p/w780{b['file_path']}",
                    'large': f"https://image.tmdb.org/t/p/w1280{b['file_path']}",
                    'original': f"https://image.tmdb.org/t/p/original{b['file_path']}"
                }
                for b in backdrops[:5]
            ]

        # Cast and crew
        credits = self.get_credits(item_id, media_type)
        if credits:
            cast = credits.get('cast', [])
            crew = credits.get('crew', [])

            enriched['cast'] = [
                {
                    'name': c['name'],
                    'character': c.get('character', ''),
                    'profile_path': f"https://image.tmdb.org/t/p/w185{c['profile_path']}" if c.get('profile_path') else None
                }
                for c in cast[:10]
            ]

            directors = [c['name'] for c in crew if c.get('job') == 'Director']
            enriched['directors'] = directors

            writers = [c['name'] for c in crew if c.get('job') in ['Writer', 'Screenplay']]
            enriched['writers'] = writers[:5]

        # Videos (trailers)
        videos = self.get_videos(item_id, media_type)
        if videos:
            trailers = [v for v in videos if v.get('type') == 'Trailer' and v.get('site') == 'YouTube']
            if trailers:
                official_trailer = next((t for t in trailers if t.get('official')), trailers[0])
                enriched['youtube_id'] = official_trailer['key']
                enriched['youtube_url'] = f"https://www.youtube.com/watch?v={official_trailer['key']}"
                enriched['youtube_title'] = official_trailer.get('name', '')

        return enriched

    def run(self):
        """Run the complete update process"""

        start_time = time.time()

        print("\n" + "="*70)
        print("TMDB-BASED CONTENT UPDATER")
        print("="*70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Date range: {self.today} to {self.end_date}")
        print(f"Region: India")
        print(f"Test mode: {'Yes (limited)' if self.test_mode else 'No'}")
        print("="*70)

        # Discover movies
        print("\n" + "="*70)
        print("STEP 1: DISCOVERING MOVIES")
        print("="*70 + "\n")
        movies = self.discover_content('movie')
        print(f"✅ Found {len(movies)} movies")

        # Discover TV shows
        print("\n" + "="*70)
        print("STEP 2: DISCOVERING TV SHOWS")
        print("="*70 + "\n")
        tv_shows = self.discover_content('tv')
        print(f"✅ Found {len(tv_shows)} TV shows")

        # Enrich all content
        print("\n" + "="*70)
        print("STEP 3: ENRICHING WITH FULL METADATA")
        print("="*70 + "\n")

        all_content = []

        # Enrich movies
        if movies:
            print(f"Enriching {len(movies)} movies...\n")
            for i, movie in enumerate(movies, 1):
                title = movie.get('title', 'Unknown')[:50]
                print(f"[{i}/{len(movies)}] {title}... ", end='', flush=True)

                try:
                    enriched = self.enrich_item(movie, 'movie')
                    all_content.append(enriched)

                    platforms = enriched.get('platforms', [])
                    if platforms:
                        print(f"✓ {len(platforms)} platform(s)")
                    else:
                        print("✓ Platform TBA")

                except Exception as e:
                    print(f"✗ Error: {str(e)[:30]}")

                time.sleep(0.3)

        # Enrich TV shows
        if tv_shows:
            print(f"\nEnriching {len(tv_shows)} TV shows...\n")
            for i, show in enumerate(tv_shows, 1):
                title = show.get('name', 'Unknown')[:50]
                print(f"[{i}/{len(tv_shows)}] {title}... ", end='', flush=True)

                try:
                    enriched = self.enrich_item(show, 'tv')
                    all_content.append(enriched)

                    platforms = enriched.get('platforms', [])
                    if platforms:
                        print(f"✓ {len(platforms)} platform(s)")
                    else:
                        print("✓ Platform TBA")

                except Exception as e:
                    print(f"✗ Error: {str(e)[:30]}")

                time.sleep(0.3)

        # Save results
        if all_content:
            with open('movies_enriched.json', 'w', encoding='utf-8') as f:
                json.dump(all_content, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Saved: movies_enriched.json")

        # Summary
        elapsed = time.time() - start_time

        platform_counts = {}
        for item in all_content:
            for platform in item.get('platforms', []):
                platform_counts[platform] = platform_counts.get(platform, 0) + 1

        with_platforms = sum(1 for item in all_content if item.get('platforms'))
        with_posters = sum(1 for item in all_content if item.get('posters'))
        with_trailers = sum(1 for item in all_content if item.get('youtube_id'))
        with_cast = sum(1 for item in all_content if item.get('cast'))

        print("\n" + "="*70)
        print("✅ UPDATE COMPLETE!")
        print("="*70)
        print(f"\n📊 Summary:")
        print(f"   • Total content: {len(all_content)}")
        print(f"   • Movies: {len(movies)}")
        print(f"   • TV shows: {len(tv_shows)}")
        print(f"   • With streaming platforms: {with_platforms}")
        print(f"   • With posters: {with_posters}")
        print(f"   • With trailers: {with_trailers}")
        print(f"   • With cast info: {with_cast}")

        if platform_counts:
            print(f"\n📺 Platform Distribution:")
            for platform, count in sorted(platform_counts.items(), key=lambda x: -x[1]):
                print(f"   • {platform}: {count}")

        print(f"\n⏱️  Time elapsed: {elapsed:.1f} seconds")
        print(f"\n📁 Output: movies_enriched.json")
        print("="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(description='Update content using TMDB API')
    parser.add_argument('--days', type=int, default=60, help='Days ahead to look (default: 60)')
    parser.add_argument('--test', action='store_true', help='Test mode (limited results)')

    args = parser.parse_args()

    updater = TMDBContentUpdater(days_ahead=args.days, test_mode=args.test)

    try:
        updater.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Update interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
