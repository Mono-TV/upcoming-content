#!/usr/bin/env python3
"""
Unified Content Update Script
Combines scraping and all enrichment steps into one script

Usage:
    python3 update_content.py [--pages N] [--no-posters] [--no-trailers]
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
    from imdb import Cinemagoer
    import requests
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("\n💡 Install required packages:")
    print("   pip3 install playwright beautifulsoup4 cinemagoer requests")
    print("   playwright install chromium")
    sys.exit(1)


class ContentUpdater:
    """Unified content scraper and enricher"""

    def __init__(self, max_pages=5, enable_posters=True, enable_trailers=True):
        self.max_pages = max_pages
        self.enable_posters = enable_posters
        self.enable_trailers = enable_trailers
        self.movies = []

        # IMDb client
        self.ia = Cinemagoer()

        # YouTube API (if available)
        self.youtube_api_key = os.environ.get('YOUTUBE_API_KEY')

        # TMDb API (if available)
        self.tmdb_api_key = os.environ.get('TMDB_API_KEY')

        # Platform mapping
        self.platform_map = {
            '4': 'Amazon Prime Video',
            '5': 'Netflix',
            '30': 'Jio Hotstar',
            '70': 'Sun NXT',
            '94': 'Manorama MAX',
            '155': 'Sony LIV'
        }

    async def scrape_movies(self):
        """Step 1: Scrape movies from Binged.com"""
        print("\n" + "="*60)
        print("STEP 1: SCRAPING MOVIES")
        print("="*60 + "\n")

        # Correct URL with platform filters
        url = "https://www.binged.com/streaming-premiere-dates/?mode=streaming-month&platform[]=Aha%20Video&platform[]=Amazon&platform[]=Apple%20Tv%20Plus&platform[]=Jio%20Hotstar&platform[]=Manorama%20MAX&platform[]=Netflix&platform[]=Sony%20LIV&platform[]=Sun%20NXT&platform[]=Zee5"

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )

            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            page = await context.new_page()

            # Add extra properties to avoid detection
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """)

            try:
                print(f"📄 Loading initial page...")
                await page.goto(url, wait_until='networkidle', timeout=30000)
                await page.wait_for_selector('.bng-movies-table-item', timeout=10000)
                await asyncio.sleep(2)

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

                # Paginate through remaining pages
                for page_num in range(2, self.max_pages + 1):
                    try:
                        # Find and click next button
                        next_button = await page.query_selector('.bng-movies-table-pagination span:has-text("Next")')
                        if not next_button:
                            print("  No more pages available")
                            break

                        print(f"\n📄 Clicking to page {page_num}...")
                        await next_button.click()

                        # Wait for content to load
                        try:
                            await page.wait_for_load_state('networkidle', timeout=10000)
                        except:
                            await asyncio.sleep(3)

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

        # Image
        image_div = item.find('div', class_='bng-movies-table-image')
        if image_div:
            img = image_div.find('img')
            if img:
                img_src = img.get('src', '')
                if img_src:
                    movie_data['image_url'] = img_src

        return movie_data if movie_data.get('title') else None

    def enrich_with_imdb(self):
        """Step 2: Enrich with IMDb data"""
        print("\n" + "="*60)
        print("STEP 2: ENRICHING WITH IMDB DATA")
        print("="*60 + "\n")

        enriched_count = 0
        for i, movie in enumerate(self.movies, 1):
            title = movie.get('title', '')
            print(f"[{i}/{len(self.movies)}] {title[:50]}... ", end='', flush=True)

            try:
                results = self.ia.search_movie(title)
                if results:
                    movie_id = results[0].movieID
                    movie['imdb_id'] = f"tt{movie_id}"

                    # Get detailed info
                    movie_info = self.ia.get_movie(movie_id)
                    if 'year' in movie_info:
                        movie['imdb_year'] = str(movie_info['year'])

                    enriched_count += 1
                    print(f"✓ {movie['imdb_id']}")
                else:
                    print("✗ Not found")

                time.sleep(0.5)  # Rate limiting

            except Exception as e:
                print(f"✗ Error: {e}")

        print(f"\n✅ Enriched {enriched_count}/{len(self.movies)} movies with IMDb data")
        self._save_json(self.movies, 'movies_with_imdb.json')

    def enrich_with_youtube(self):
        """Step 3: Add YouTube trailers"""
        if not self.enable_trailers:
            print("\n⏭️  Skipping YouTube enrichment")
            return

        print("\n" + "="*60)
        print("STEP 3: FINDING YOUTUBE TRAILERS")
        print("="*60 + "\n")

        enriched_count = 0
        for i, movie in enumerate(self.movies, 1):
            title = movie.get('title', '')
            year = movie.get('imdb_year', '')
            search_query = f"{title} {year} official trailer" if year else f"{title} official trailer"

            print(f"[{i}/{len(self.movies)}] {title[:40]}... ", end='', flush=True)

            try:
                if self.youtube_api_key:
                    # Use YouTube API
                    url = "https://www.googleapis.com/youtube/v3/search"
                    params = {
                        'part': 'snippet',
                        'q': search_query,
                        'type': 'video',
                        'maxResults': 1,
                        'key': self.youtube_api_key
                    }
                    response = requests.get(url, params=params, timeout=10)
                    data = response.json()

                    if 'items' in data and len(data['items']) > 0:
                        video_id = data['items'][0]['id']['videoId']
                        video_title = data['items'][0]['snippet']['title']
                        movie['youtube_id'] = video_id
                        movie['youtube_url'] = f"https://www.youtube.com/watch?v={video_id}"
                        movie['youtube_title'] = video_title
                        enriched_count += 1
                        print(f"✓ {video_id}")
                    else:
                        print("✗ Not found")
                else:
                    # Fallback: Use YouTube search URL pattern
                    search_url = f"https://www.youtube.com/results?search_query={requests.utils.quote(search_query)}"
                    response = requests.get(search_url, timeout=10)

                    # Basic parsing for video ID
                    match = re.search(r'"videoId":"([^"]+)"', response.text)
                    if match:
                        video_id = match.group(1)
                        movie['youtube_id'] = video_id
                        movie['youtube_url'] = f"https://www.youtube.com/watch?v={video_id}"
                        enriched_count += 1
                        print(f"✓ {video_id}")
                    else:
                        print("✗ Not found")

                time.sleep(0.3)  # Rate limiting

            except Exception as e:
                print(f"✗ Error: {e}")

        print(f"\n✅ Found trailers for {enriched_count}/{len(self.movies)} movies")
        self._save_json(self.movies, 'movies_with_trailers.json')

    def enrich_with_posters(self):
        """Step 4: Add high-quality posters from TMDb"""
        if not self.enable_posters or not self.tmdb_api_key:
            print("\n⏭️  Skipping poster enrichment")
            if not self.tmdb_api_key:
                print("💡 Set TMDB_API_KEY environment variable to enable posters")
            return

        print("\n" + "="*60)
        print("STEP 4: ADDING HIGH-QUALITY POSTERS")
        print("="*60 + "\n")

        enriched_count = 0
        for i, movie in enumerate(self.movies, 1):
            title = movie.get('title', '')
            year = movie.get('imdb_year', '')

            print(f"[{i}/{len(self.movies)}] {title[:40]}... ", end='', flush=True)

            try:
                # Search TMDb
                url = "https://api.themoviedb.org/3/search/multi"
                params = {
                    'api_key': self.tmdb_api_key,
                    'query': title,
                    'year': year if year else None
                }
                response = requests.get(url, params=params, timeout=10)
                data = response.json()

                if 'results' in data and len(data['results']) > 0:
                    result = data['results'][0]
                    poster_path = result.get('poster_path')

                    if poster_path:
                        movie['poster_url_medium'] = f"https://image.tmdb.org/t/p/w500{poster_path}"
                        movie['poster_url_large'] = f"https://image.tmdb.org/t/p/original{poster_path}"
                        movie['tmdb_id'] = result.get('id')
                        movie['tmdb_media_type'] = result.get('media_type')
                        enriched_count += 1
                        print("✓ Poster added")
                    else:
                        print("✗ No poster")
                else:
                    print("✗ Not found")

                time.sleep(0.3)  # Rate limiting

            except Exception as e:
                print(f"✗ Error: {e}")

        print(f"\n✅ Added posters for {enriched_count}/{len(self.movies)} movies")
        self._save_json(self.movies, 'movies_enriched.json')

    def _save_json(self, data, filename):
        """Save data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved: {filename}")

    async def run(self):
        """Run all steps"""
        start_time = time.time()

        print("\n" + "="*60)
        print("UNIFIED CONTENT UPDATER")
        print("="*60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

        # Step 1: Scrape
        await self.scrape_movies()

        # Step 2: IMDb enrichment
        if self.movies:
            self.enrich_with_imdb()

        # Step 3: YouTube trailers
        if self.movies:
            self.enrich_with_youtube()

        # Step 4: TMDb posters
        if self.movies:
            self.enrich_with_posters()

        # Summary
        elapsed = time.time() - start_time
        print("\n" + "="*60)
        print("✅ ALL DONE!")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"   • Movies scraped: {len(self.movies)}")
        print(f"   • Time elapsed: {elapsed:.1f} seconds")
        print(f"\n📁 Files created:")
        print(f"   • movies.json")
        print(f"   • movies_with_imdb.json")
        if self.enable_trailers:
            print(f"   • movies_with_trailers.json")
        if self.enable_posters and self.tmdb_api_key:
            print(f"   • movies_enriched.json")
        print("\n" + "="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description='Unified movie scraper and enricher')
    parser.add_argument('--pages', type=int, default=5, help='Number of pages to scrape (default: 5)')
    parser.add_argument('--no-trailers', action='store_true', help='Skip YouTube trailer enrichment')
    parser.add_argument('--no-posters', action='store_true', help='Skip TMDb poster enrichment')

    args = parser.parse_args()

    updater = ContentUpdater(
        max_pages=args.pages,
        enable_trailers=not args.no_trailers,
        enable_posters=not args.no_posters
    )

    asyncio.run(updater.run())


if __name__ == '__main__':
    main()
