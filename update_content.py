#!/usr/bin/env python3
"""
Unified Content Update Script - TMDB-Focused
Fetches comprehensive metadata from TMDB including all posters, backdrops, cast, genres, etc.

Usage:
    python3 update_content.py [--pages N] [--no-trailers] [--test]
"""

import asyncio
import json
import re
import sys
import os
import time
import argparse
from typing import List, Dict, Optional
from datetime import datetime

# Check required packages
try:
    from playwright.async_api import async_playwright
    from bs4 import BeautifulSoup
    import requests
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("\n💡 Install required packages:")
    print("   pip3 install playwright beautifulsoup4 requests")
    print("   playwright install chromium")
    sys.exit(1)


class TMDBContentUpdater:
    """Content scraper with comprehensive TMDB enrichment"""

    def __init__(self, max_pages=5, enable_trailers=True, test_mode=False):
        self.max_pages = max_pages
        self.enable_trailers = enable_trailers
        self.test_mode = test_mode
        self.movies = []

        # TMDB API (required)
        self.tmdb_api_key = os.environ.get('TMDB_API_KEY')
        if not self.tmdb_api_key:
            print("\n" + "="*60)
            print("❌ TMDB API KEY REQUIRED")
            print("="*60)
            print("\nThis script requires a TMDB API key to fetch comprehensive metadata.")
            print("\n💡 Get your free API key:")
            print("   1. Visit: https://www.themoviedb.org/settings/api")
            print("   2. Sign up for a free account")
            print("   3. Request an API key")
            print("   4. Set environment variable:")
            print("      export TMDB_API_KEY='your_key_here'")
            print("\n" + "="*60 + "\n")
            sys.exit(1)

        # YouTube API (optional)
        self.youtube_api_key = os.environ.get('YOUTUBE_API_KEY')

        # Platform mapping
        self.platform_map = {
            '4': 'Amazon Prime Video',
            '5': 'Apple TV+',
            '10': 'Jio Hotstar',
            '27': 'Manorama MAX',
            '30': 'Netflix',
            '52': 'Zee5',
            '70': 'Sun NXT',
            '94': 'Manorama MAX',
            '155': 'Sony LIV'
        }

    async def scrape_movies(self):
        """Step 1: Scrape movies from Binged.com"""
        print("\n" + "="*60)
        print("STEP 1: SCRAPING MOVIES FROM BINGED.COM")
        print("="*60 + "\n")

        url = "https://www.binged.com/streaming-premiere-dates/?mode=streaming-soon-month&platform[]=Aha%20Video&platform[]=Amazon&platform[]=Apple%20Tv%20Plus&platform[]=Jio%20Hotstar&platform[]=Manorama%20MAX&platform[]=Netflix&platform[]=Sony%20LIV&platform[]=Sun%20NXT&platform[]=Zee5"

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )

            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )

            page = await context.new_page()

            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """)

            try:
                print(f"📄 Loading initial page...")
                await page.goto(url, wait_until='domcontentloaded', timeout=60000)
                await page.wait_for_selector('.bng-movies-table-item', timeout=15000)
                await asyncio.sleep(3)

                current_page = 1

                # Scrape first page
                print(f"Scraping page {current_page}...")
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')

                movie_items = soup.find_all('div', class_='bng-movies-table-item')
                movie_items = [item for item in movie_items
                               if not item.find('div', class_='bng-movies-table-item-th')
                               and not item.find('div', class_='bng-movies-table-item-preloader')]

                print(f"  Found {len(movie_items)} entries")

                for item in movie_items:
                    movie_data = self._parse_movie_item(item)
                    if movie_data and movie_data.get('title'):
                        self.movies.append(movie_data)

                # Paginate
                for page_num in range(2, self.max_pages + 1):
                    try:
                        next_button = await page.query_selector('.bng-movies-table-pagination span:has-text("Next")')
                        if not next_button:
                            print("  No more pages available")
                            break

                        print(f"\n📄 Clicking to page {page_num}...")
                        await next_button.click()

                        try:
                            await page.wait_for_load_state('domcontentloaded', timeout=15000)
                            await asyncio.sleep(2)
                        except:
                            await asyncio.sleep(4)

                        current_page = page_num
                        print(f"Scraping page {current_page}...")

                        content = await page.content()
                        soup = BeautifulSoup(content, 'html.parser')

                        movie_items = soup.find_all('div', class_='bng-movies-table-item')
                        movie_items = [item for item in movie_items
                                       if not item.find('div', class_='bng-movies-table-item-th')
                                       and not item.find('div', class_='bng-movies-table-item-preloader')]

                        print(f"  Found {len(movie_items)} entries")

                        if not movie_items:
                            print("  No movies found, stopping")
                            break

                        for item in movie_items:
                            movie_data = self._parse_movie_item(item)
                            if movie_data and movie_data.get('title'):
                                self.movies.append(movie_data)

                    except Exception as e:
                        print(f"  ⚠️  Error on page {page_num}: {e}")
                        break

            except Exception as e:
                print(f"  ⚠️  Error during scraping: {e}")

            await browser.close()

        print(f"\n✅ Scraped {len(self.movies)} movies total")
        self._save_json(self.movies, 'movies.json')

    def _parse_movie_item(self, item) -> Optional[Dict]:
        """Parse a single movie item from HTML"""
        movie_data = {}

        # Title
        title_div = item.find('div', class_='bng-movies-table-item-title')
        if title_div:
            link = title_div.find('a')
            if link:
                title_text = link.get_text(separator='|', strip=True).split('|')[0].strip()
                title_text = title_text.replace('\n', ' ').strip()
                if title_text:
                    movie_data['title'] = title_text
                href = link.get('href', '')
                if href:
                    movie_data['url'] = href

        # Release date
        date_div = item.find('div', class_='bng-movies-table-date')
        if date_div:
            date_span = date_div.find('span')
            if date_span:
                date_text = date_span.get_text(strip=True)
                if date_text:
                    movie_data['release_date'] = date_text

        # Platforms
        platform_div = item.find('div', class_='bng-movies-table-platform')
        if platform_div:
            platform_container = platform_div.find('div', class_='streaming-item-platform')
            if platform_container:
                platform_imgs = platform_container.find_all('img')
                platforms = []
                for img in platform_imgs:
                    src = img.get('src', '')
                    match = re.search(r'/(\d+)\.(webp|png)', src)
                    if match:
                        platform_id = match.group(1)
                        platform_name = self.platform_map.get(platform_id, f'Platform {platform_id}')
                        if platform_name not in platforms:
                            platforms.append(platform_name)
                if platforms:
                    movie_data['platforms'] = platforms

        return movie_data if movie_data.get('title') else None

    def _extract_language_from_url(self, url):
        """Extract language from Binged URL"""
        if not url:
            return None

        language_patterns = {
            'hindi': 'Hindi', 'tamil': 'Tamil', 'telugu': 'Telugu',
            'malayalam': 'Malayalam', 'kannada': 'Kannada', 'bengali': 'Bengali',
            'marathi': 'Marathi', 'punjabi': 'Punjabi', 'gujarati': 'Gujarati',
            'korean': 'Korean', 'japanese': 'Japanese', 'mandarin': 'Chinese',
            'spanish': 'Spanish', 'french': 'French', 'german': 'German',
            'italian': 'Italian', 'portuguese': 'Portuguese', 'russian': 'Russian'
        }

        url_lower = url.lower()
        for pattern, language in language_patterns.items():
            if f'-{pattern}-' in url_lower or f'/{pattern}-' in url_lower:
                return language

        return None

    def _clean_title_for_search(self, title):
        """Clean up title for better search results"""
        if not title:
            return title

        cleaned = title
        cleaned = re.sub(r'\([^)]*\)', '', cleaned)  # Remove parentheses
        cleaned = ' '.join(cleaned.split())  # Remove extra whitespace
        cleaned = cleaned.strip(' -:')  # Remove trailing punctuation

        return cleaned

    def _fetch_with_retry(self, url, params, max_retries=3):
        """Fetch URL with retry logic"""
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                return response.json()
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    time.sleep(wait_time)
                    continue
                else:
                    raise
            except Exception:
                raise

    def _search_tmdb(self, movie: Dict) -> Optional[Dict]:
        """Search TMDB with multiple strategies"""
        title = movie.get('title', '')
        url = movie.get('url', '')

        language = self._extract_language_from_url(url)
        clean_title = self._clean_title_for_search(title)

        # Try multiple search strategies
        search_queries = []

        # Strategy 1: Title + Language
        if language:
            search_queries.append(f"{clean_title} {language}")

        # Strategy 2: Clean title only
        search_queries.append(clean_title)

        # Strategy 3: Original title
        if clean_title != title:
            search_queries.append(title)

        # Strategy 4: For TV shows, try without "Season X"
        if 'Season' in title:
            base_title = re.sub(r'\s+Season\s+\d+.*', '', title, flags=re.IGNORECASE).strip()
            search_queries.append(base_title)
            if language:
                search_queries.append(f"{base_title} {language}")

        for query in search_queries:
            try:
                url = "https://api.themoviedb.org/3/search/multi"
                params = {
                    'api_key': self.tmdb_api_key,
                    'query': query,
                    'language': 'en-US'
                }

                data = self._fetch_with_retry(url, params)

                if data.get('results') and len(data['results']) > 0:
                    return data['results'][0]
            except:
                continue

        return None

    async def _fetch_binged_poster(self, movie: Dict) -> Optional[str]:
        """Fallback: Fetch poster from Binged.com content page"""
        url = movie.get('url')
        if not url:
            return None

        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                await page.goto(url, wait_until='domcontentloaded', timeout=15000)
                await asyncio.sleep(1)

                content = await page.content()
                await browser.close()

                soup = BeautifulSoup(content, 'html.parser')

                # Try multiple selectors for poster
                poster_selectors = [
                    'img.movie-poster', 'img.show-poster',
                    '.movie-image img', '.show-image img',
                    'img[alt*="poster"]', 'img[alt*="Poster"]'
                ]

                for selector in poster_selectors:
                    img = soup.select_one(selector)
                    if img:
                        poster_url = img.get('src') or img.get('data-src')
                        if poster_url and poster_url.startswith('http'):
                            return poster_url

                # Try og:image
                og_image = soup.find('meta', property='og:image')
                if og_image:
                    poster_url = og_image.get('content')
                    if poster_url and poster_url.startswith('http'):
                        return poster_url

        except:
            pass

        return None

    async def enrich_with_tmdb_comprehensive(self):
        """
        Step 2: Comprehensive TMDB Enrichment
        Fetches all available metadata:
        - Multiple poster sizes (vertical posters)
        - Multiple backdrop sizes
        - Full movie/show details (description, genres, runtime, etc.)
        - Cast and crew
        - IMDb ID
        - Videos (trailers)
        - Fallback to Binged.com posters if TMDB doesn't have content
        """
        print("\n" + "="*60)
        print("STEP 2: COMPREHENSIVE TMDB ENRICHMENT WITH FALLBACKS")
        print("="*60 + "\n")

        enriched_count = 0

        for i, movie in enumerate(self.movies, 1):
            title = movie.get('title', '')

            print(f"[{i}/{len(self.movies)}] {title[:50]}... ", end='', flush=True)

            try:
                # 2a. Search TMDB
                tmdb_result = self._search_tmdb(movie)

                if not tmdb_result:
                    # Fallback: Try to get poster from Binged.com
                    binged_poster = await self._fetch_binged_poster(movie)
                    if binged_poster:
                        movie['poster_url_medium'] = binged_poster
                        movie['poster_url_large'] = binged_poster
                        movie['posters'] = {
                            'thumbnail': binged_poster,
                            'small': binged_poster,
                            'medium': binged_poster,
                            'large': binged_poster,
                            'xlarge': binged_poster,
                            'original': binged_poster
                        }
                        print("⊙ Binged poster only")
                    else:
                        print("✗ Not found (no poster)")
                    continue

                tmdb_id = tmdb_result['id']
                media_type = tmdb_result.get('media_type', 'movie')

                # Store basic TMDB data
                movie['tmdb_id'] = tmdb_id
                movie['tmdb_media_type'] = media_type

                # 2b. Get full details
                details = self._get_tmdb_details(tmdb_id, media_type)
                if details:
                    # Overview/Description
                    movie['overview'] = details.get('overview', '')
                    movie['description'] = details.get('overview', '')  # Alias

                    # Genres
                    genres = details.get('genres', [])
                    movie['genres'] = [g['name'] for g in genres]

                    # Runtime (for movies)
                    if media_type == 'movie':
                        movie['runtime'] = details.get('runtime')

                    # Episode runtime (for TV shows)
                    if media_type == 'tv':
                        movie['episode_runtime'] = details.get('episode_run_time', [])
                        movie['number_of_seasons'] = details.get('number_of_seasons')
                        movie['number_of_episodes'] = details.get('number_of_episodes')

                    # Release info
                    movie['tmdb_release_date'] = details.get('release_date') or details.get('first_air_date')
                    movie['status'] = details.get('status')

                    # Ratings
                    movie['tmdb_rating'] = details.get('vote_average')
                    movie['tmdb_vote_count'] = details.get('vote_count')

                    # Original title and language
                    movie['original_title'] = details.get('original_title') or details.get('original_name')
                    movie['original_language'] = details.get('original_language')

                # 2c. Get external IDs (IMDb)
                external_ids = self._get_tmdb_external_ids(tmdb_id, media_type)
                if external_ids:
                    imdb_id = external_ids.get('imdb_id')
                    if imdb_id:
                        movie['imdb_id'] = imdb_id

                # 2d. Get all posters (multiple sizes)
                posters = self._get_tmdb_images(tmdb_id, media_type, 'posters')
                if posters:
                    movie['posters'] = {
                        'thumbnail': f"https://image.tmdb.org/t/p/w92{posters[0]}",
                        'small': f"https://image.tmdb.org/t/p/w185{posters[0]}",
                        'medium': f"https://image.tmdb.org/t/p/w342{posters[0]}",
                        'large': f"https://image.tmdb.org/t/p/w500{posters[0]}",
                        'xlarge': f"https://image.tmdb.org/t/p/w780{posters[0]}",
                        'original': f"https://image.tmdb.org/t/p/original{posters[0]}"
                    }

                    # Also store all available posters
                    movie['all_posters'] = [
                        {
                            'thumbnail': f"https://image.tmdb.org/t/p/w92{p}",
                            'small': f"https://image.tmdb.org/t/p/w185{p}",
                            'medium': f"https://image.tmdb.org/t/p/w342{p}",
                            'large': f"https://image.tmdb.org/t/p/w500{p}",
                            'xlarge': f"https://image.tmdb.org/t/p/w780{p}",
                            'original': f"https://image.tmdb.org/t/p/original{p}"
                        }
                        for p in posters[:5]  # Limit to top 5 posters
                    ]

                    # Legacy fields for backward compatibility
                    movie['poster_url_medium'] = movie['posters']['medium']
                    movie['poster_url_large'] = movie['posters']['large']
                else:
                    # Fallback: Try Binged.com if TMDB has no posters
                    binged_poster = await self._fetch_binged_poster(movie)
                    if binged_poster:
                        movie['poster_url_medium'] = binged_poster
                        movie['poster_url_large'] = binged_poster
                        movie['posters'] = {
                            'thumbnail': binged_poster,
                            'small': binged_poster,
                            'medium': binged_poster,
                            'large': binged_poster,
                            'xlarge': binged_poster,
                            'original': binged_poster
                        }
                        movie['poster_source'] = 'binged'

                # 2e. Get all backdrops
                backdrops = self._get_tmdb_images(tmdb_id, media_type, 'backdrops')
                if backdrops:
                    movie['backdrops'] = {
                        'small': f"https://image.tmdb.org/t/p/w300{backdrops[0]}",
                        'medium': f"https://image.tmdb.org/t/p/w780{backdrops[0]}",
                        'large': f"https://image.tmdb.org/t/p/w1280{backdrops[0]}",
                        'original': f"https://image.tmdb.org/t/p/original{backdrops[0]}"
                    }

                    # All available backdrops
                    movie['all_backdrops'] = [
                        {
                            'small': f"https://image.tmdb.org/t/p/w300{b}",
                            'medium': f"https://image.tmdb.org/t/p/w780{b}",
                            'large': f"https://image.tmdb.org/t/p/w1280{b}",
                            'original': f"https://image.tmdb.org/t/p/original{b}"
                        }
                        for b in backdrops[:5]  # Limit to top 5
                    ]

                    # Legacy field
                    movie['backdrop_url'] = movie['backdrops']['original']

                # 2f. Get cast and crew
                credits = self._get_tmdb_credits(tmdb_id, media_type)
                if credits:
                    cast = credits.get('cast', [])
                    crew = credits.get('crew', [])

                    # Top cast members
                    movie['cast'] = [
                        {
                            'name': c['name'],
                            'character': c.get('character', ''),
                            'profile_path': f"https://image.tmdb.org/t/p/w185{c['profile_path']}" if c.get('profile_path') else None
                        }
                        for c in cast[:10]  # Top 10 cast
                    ]

                    # Directors
                    directors = [c['name'] for c in crew if c.get('job') == 'Director']
                    movie['directors'] = directors

                    # Writers
                    writers = [c['name'] for c in crew if c.get('job') in ['Writer', 'Screenplay']]
                    movie['writers'] = writers[:5]  # Top 5

                # 2g. Get videos (trailers from TMDB)
                videos = self._get_tmdb_videos(tmdb_id, media_type)
                if videos:
                    trailers = [v for v in videos if v.get('type') == 'Trailer' and v.get('site') == 'YouTube']
                    if trailers:
                        # Use official trailer
                        official_trailer = next((t for t in trailers if t.get('official')), trailers[0])
                        movie['youtube_id'] = official_trailer['key']
                        movie['youtube_url'] = f"https://www.youtube.com/watch?v={official_trailer['key']}"
                        movie['youtube_title'] = official_trailer.get('name', '')

                enriched_count += 1
                print(f"✓ Complete")

                time.sleep(0.25)  # Rate limiting

            except Exception as e:
                print(f"✗ Error: {str(e)[:40]}")

        print(f"\n✅ Enriched {enriched_count}/{len(self.movies)} movies with comprehensive TMDB data")
        self._save_json(self.movies, 'movies_enriched.json')

    def _get_tmdb_details(self, tmdb_id: int, media_type: str) -> Optional[Dict]:
        """Get full movie/show details from TMDB"""
        try:
            url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}"
            params = {
                'api_key': self.tmdb_api_key,
                'language': 'en-US'
            }
            return self._fetch_with_retry(url, params)
        except:
            return None

    def _get_tmdb_external_ids(self, tmdb_id: int, media_type: str) -> Optional[Dict]:
        """Get external IDs (IMDb, etc.) from TMDB"""
        try:
            url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/external_ids"
            params = {'api_key': self.tmdb_api_key}
            return self._fetch_with_retry(url, params)
        except:
            return None

    def _get_tmdb_images(self, tmdb_id: int, media_type: str, image_type: str) -> List[str]:
        """Get all images (posters or backdrops) from TMDB"""
        try:
            url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/images"
            params = {'api_key': self.tmdb_api_key}

            data = self._fetch_with_retry(url, params)

            if image_type == 'posters':
                images = data.get('posters', [])
            else:
                images = data.get('backdrops', [])

            # Sort by vote average (quality)
            images.sort(key=lambda x: x.get('vote_average', 0), reverse=True)

            # Return file paths
            return [img['file_path'] for img in images if img.get('file_path')]

        except:
            return []

    def _get_tmdb_credits(self, tmdb_id: int, media_type: str) -> Optional[Dict]:
        """Get cast and crew from TMDB"""
        try:
            url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/credits"
            params = {'api_key': self.tmdb_api_key}
            return self._fetch_with_retry(url, params)
        except:
            return None

    def _get_tmdb_videos(self, tmdb_id: int, media_type: str) -> List[Dict]:
        """Get videos (trailers) from TMDB"""
        try:
            url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/videos"
            params = {
                'api_key': self.tmdb_api_key,
                'language': 'en-US'
            }
            data = self._fetch_with_retry(url, params)
            return data.get('results', [])
        except:
            return []

    def _save_json(self, data, filename):
        """Save data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved: {filename}")

    async def run(self):
        """Run all steps"""
        start_time = time.time()

        print("\n" + "="*60)
        print("COMPREHENSIVE TMDB CONTENT UPDATER")
        print("="*60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

        # Step 1: Scrape from Binged
        await self.scrape_movies()

        # Test mode: limit to first 3 movies
        if self.test_mode and len(self.movies) > 3:
            print(f"\n🧪 TEST MODE: Processing only first 3 movies (out of {len(self.movies)})")
            self.movies = self.movies[:3]

        # Step 2: Comprehensive TMDB Enrichment
        if self.movies:
            await self.enrich_with_tmdb_comprehensive()

        # Summary
        elapsed = time.time() - start_time

        with_tmdb = sum(1 for m in self.movies if m.get('tmdb_id'))
        with_imdb = sum(1 for m in self.movies if m.get('imdb_id'))
        with_posters = sum(1 for m in self.movies if m.get('posters'))
        with_backdrops = sum(1 for m in self.movies if m.get('backdrops'))
        with_cast = sum(1 for m in self.movies if m.get('cast'))
        with_genres = sum(1 for m in self.movies if m.get('genres'))
        with_description = sum(1 for m in self.movies if m.get('overview'))
        with_trailers = sum(1 for m in self.movies if m.get('youtube_id'))

        print("\n" + "="*60)
        print("✅ ALL DONE!")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"   • Movies scraped: {len(self.movies)}")
        print(f"   • With TMDB IDs: {with_tmdb}/{len(self.movies)}")
        print(f"   • With IMDb IDs: {with_imdb}/{len(self.movies)}")
        print(f"   • With descriptions: {with_description}/{len(self.movies)}")
        print(f"   • With genres: {with_genres}/{len(self.movies)}")
        print(f"   • With cast info: {with_cast}/{len(self.movies)}")
        print(f"   • With posters: {with_posters}/{len(self.movies)}")
        print(f"   • With backdrops: {with_backdrops}/{len(self.movies)}")
        print(f"   • With trailers: {with_trailers}/{len(self.movies)}")
        print(f"   • Time elapsed: {elapsed:.1f} seconds")
        print(f"\n📁 Files created:")
        print(f"   • movies.json (scraped data)")
        print(f"   • movies_enriched.json (✨ FINAL - comprehensive TMDB data)")
        print("\n" + "="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description='Comprehensive TMDB movie scraper and enricher')
    parser.add_argument('--pages', type=int, default=5, help='Number of pages to scrape (default: 5)')
    parser.add_argument('--no-trailers', action='store_true', help='Skip trailer enrichment')
    parser.add_argument('--test', action='store_true', help='Test mode: process only 3 movies')

    args = parser.parse_args()

    updater = TMDBContentUpdater(
        max_pages=args.pages,
        enable_trailers=not args.no_trailers,
        test_mode=args.test
    )

    asyncio.run(updater.run())


if __name__ == '__main__':
    main()
