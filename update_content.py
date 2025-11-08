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
    """Unified content scraper and enricher with safety measures"""

    def __init__(self, max_pages=5, enable_posters=True, enable_trailers=True, test_mode=False):
        self.max_pages = max_pages
        self.enable_posters = enable_posters
        self.enable_trailers = enable_trailers
        self.test_mode = test_mode
        self.movies = []

        # IMDb client
        self.ia = Cinemagoer()

        # YouTube API (if available)
        self.youtube_api_key = os.environ.get('YOUTUBE_API_KEY')

        # TMDb API (if available)
        self.tmdb_api_key = os.environ.get('TMDB_API_KEY')

        # Load manual corrections
        self.manual_corrections = self._load_manual_corrections()

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

        # Poster (from Binged - primary source)
        image_div = item.find('div', class_='bng-movies-table-image')
        if image_div:
            img = image_div.find('img')
            if img:
                # Try different attributes (data-src for lazy loading, then src)
                # Also check srcset for higher quality images
                img_src = img.get('data-src', '') or img.get('src', '') or img.get('data-lazy-src', '')

                # Check srcset for potentially higher quality images
                srcset = img.get('srcset', '')
                if srcset and not img_src:
                    # srcset format: "url1 1x, url2 2x" - take the highest resolution
                    srcset_parts = srcset.split(',')
                    if srcset_parts:
                        # Take the last one (usually highest quality)
                        img_src = srcset_parts[-1].strip().split()[0]

                if img_src:
                    # Handle relative URLs
                    if not img_src.startswith('http'):
                        if img_src.startswith('//'):
                            img_src = 'https:' + img_src
                        elif img_src.startswith('/'):
                            img_src = 'https://www.binged.com' + img_src
                        else:
                            img_src = 'https://www.binged.com/' + img_src

                    # Only save if it looks like a valid URL
                    if img_src.startswith('http') and not img_src.endswith('.svg'):
                        movie_data['poster_url_binged'] = img_src
                        # Set as fallback poster
                        movie_data['poster_url_medium'] = img_src
                        movie_data['poster_url_large'] = img_src

        return movie_data if movie_data.get('title') else None

    def enrich_with_imdb(self):
        """Step 4: Fill missing IMDb data (optional)"""
        print("\n" + "="*60)
        print("STEP 4: IMDB DATA (FILL MISSING INFO)")
        print("="*60 + "\n")

        enriched_count = 0
        manual_count = 0

        for i, movie in enumerate(self.movies, 1):
            title = movie.get('title', '')
            print(f"[{i}/{len(self.movies)}] {title[:50]}... ", end='', flush=True)

            # Check for manual correction first
            if title in self.manual_corrections:
                correction = self.manual_corrections[title]
                movie['imdb_id'] = correction.get('imdb_id')
                movie['imdb_year'] = correction.get('imdb_year')
                enriched_count += 1
                manual_count += 1
                print(f"✓ {movie['imdb_id']} (manual)")
                continue

            try:
                # Extract language for better search
                language = self._extract_language_from_url(movie.get('url', ''))
                search_query = f"{title} {language}" if language else title

                results = self.ia.search_movie(search_query)
                if results and len(results) > 0:
                    movie_id = results[0].movieID
                    movie['imdb_id'] = f"tt{movie_id}"

                    # Get detailed info
                    try:
                        movie_info = self.ia.get_movie(movie_id)
                        if 'year' in movie_info:
                            movie['imdb_year'] = str(movie_info['year'])
                    except:
                        pass  # Year is optional

                    enriched_count += 1
                    print(f"✓ {movie['imdb_id']}")
                else:
                    # IMDb not found - not critical, skip quietly
                    print("⊘ Skipped")

                time.sleep(0.5)  # Rate limiting

            except Exception as e:
                # IMDb errors are not critical - site works without it
                print(f"⊘ Skipped ({str(e)[:20]})")

        print(f"\n✅ Enriched {enriched_count}/{len(self.movies)} movies with IMDb data")
        if manual_count > 0:
            print(f"   📋 {manual_count} from manual corrections")
        self._save_json(self.movies, 'movies_with_imdb.json')

    def _load_manual_corrections(self):
        """Load manual corrections for problematic titles"""
        try:
            if os.path.exists('manual_corrections.json'):
                with open('manual_corrections.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    corrections = data.get('corrections', {})
                    if corrections:
                        print(f"📋 Loaded {len(corrections)} manual corrections")
                    return corrections
        except Exception as e:
            print(f"⚠️  Could not load manual_corrections.json: {e}")
        return {}

    def _validate_poster_url(self, url):
        """Test if a poster URL is accessible"""
        if not url:
            return False
        try:
            response = requests.head(url, timeout=5)
            return response.status_code == 200
        except:
            return False

    def _fetch_with_retry(self, url, params, max_retries=3):
        """Fetch URL with retry logic and exponential backoff"""
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                return response.json()
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # 2s, 4s, 6s
                    time.sleep(wait_time)
                    continue
                else:
                    raise e
            except Exception as e:
                raise e

    def _clean_title_for_search(self, title):
        """Clean up title for better search results"""
        if not title:
            return title

        # Remove common patterns that might confuse search
        cleaned = title
        # Remove content in parentheses (often languages or years)
        cleaned = re.sub(r'\([^)]*\)', '', cleaned)
        # Remove extra whitespace
        cleaned = ' '.join(cleaned.split())
        # Remove trailing punctuation
        cleaned = cleaned.strip(' -:')

        return cleaned

    def _extract_language_from_url(self, url):
        """Extract language from Binged URL for better search accuracy"""
        if not url:
            return None

        # Common language patterns in URLs
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

    def enrich_with_youtube(self):
        """Step 3: Add YouTube trailers with improved search using metadata"""
        if not self.enable_trailers:
            print("\n⏭️  Skipping YouTube enrichment")
            return

        print("\n" + "="*60)
        print("STEP 3: YOUTUBE TRAILERS")
        print("="*60 + "\n")

        enriched_count = 0
        for i, movie in enumerate(self.movies, 1):
            title = movie.get('title', '')
            year = movie.get('imdb_year', '')
            url = movie.get('url', '')
            imdb_id = movie.get('imdb_id', '')

            # If we have IMDb ID but no year, try to fetch year
            if imdb_id and not year:
                try:
                    movie_id = imdb_id.replace('tt', '')
                    movie_info = self.ia.get_movie(movie_id)
                    if 'year' in movie_info:
                        year = str(movie_info['year'])
                        movie['imdb_year'] = year
                except:
                    pass

            # Extract language from URL for better specificity
            language = self._extract_language_from_url(url)

            # Clean title for better search
            clean_title = self._clean_title_for_search(title)

            # Build intelligent search query with available metadata
            search_parts = [clean_title]
            if language:
                search_parts.append(language)
            if year:
                search_parts.append(year)
            search_parts.append('official trailer')

            search_query = ' '.join(search_parts)

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
        """Step 4: Add high-quality posters from TMDb (with validation)"""
        if not self.enable_posters:
            print("\n⏭️  Skipping poster enrichment (disabled)")
            return

        if not self.tmdb_api_key:
            print("\n" + "="*60)
            print("⏭️  STEP 4: Skipping poster enrichment")
            print("="*60)
            print("\n💡 To add high-quality posters:")
            print("   1. Get free API key: https://www.themoviedb.org/settings/api")
            print("   2. Set: export TMDB_API_KEY='your_key'")
            print("   3. Re-run this script")
            print("")
            return

        print("\n" + "="*60)
        print("STEP 2: TMDB ENRICHMENT (UPGRADE POSTERS + METADATA)")
        print("="*60 + "\n")

        enriched_count = 0
        manual_count = 0
        validated_count = 0
        imdb_fallback_count = 0
        binged_kept_count = 0

        for i, movie in enumerate(self.movies, 1):
            title = movie.get('title', '')
            year = movie.get('imdb_year', '')
            has_binged_poster = bool(movie.get('poster_url_binged'))

            print(f"[{i}/{len(self.movies)}] {title[:40]}... ", end='', flush=True)

            # Check for manual correction first
            if title in self.manual_corrections:
                correction = self.manual_corrections[title]
                if 'tmdb_id' in correction:
                    # Fetch poster from specific TMDb ID with retry
                    try:
                        tmdb_id = correction['tmdb_id']
                        media_type = correction.get('tmdb_media_type', 'movie')
                        url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}"
                        params = {'api_key': self.tmdb_api_key}

                        data = self._fetch_with_retry(url, params)

                        poster_path = data.get('poster_path')
                        if poster_path:
                            poster_medium = f"https://image.tmdb.org/t/p/w500{poster_path}"
                            poster_large = f"https://image.tmdb.org/t/p/original{poster_path}"

                            # Validate poster URL
                            if self._validate_poster_url(poster_medium):
                                movie['poster_url_medium'] = poster_medium
                                movie['poster_url_large'] = poster_large
                                movie['tmdb_id'] = tmdb_id
                                movie['tmdb_media_type'] = media_type
                                enriched_count += 1
                                manual_count += 1
                                validated_count += 1
                                print("✓ Poster added (manual, validated)")
                            else:
                                print("✗ Poster URL invalid")
                        else:
                            print("✗ No poster in TMDb")
                    except Exception as e:
                        print(f"✗ Error: {str(e)[:50]}")

                    time.sleep(1.0)  # Rate limiting
                    continue

            try:
                # Extract language for better search
                language = self._extract_language_from_url(movie.get('url', ''))

                # Clean title for better search results
                clean_title = self._clean_title_for_search(title)
                search_query = f"{clean_title} {language}" if language else clean_title

                # Search TMDb with language context and retry logic
                url = "https://api.themoviedb.org/3/search/multi"
                params = {
                    'api_key': self.tmdb_api_key,
                    'query': search_query,
                    'year': year if year else None
                }

                data = self._fetch_with_retry(url, params)

                # If no results and we used language, try again without it
                if (not data.get('results') or len(data['results']) == 0) and language:
                    time.sleep(0.5)  # Small delay before retry
                    params['query'] = clean_title
                    data = self._fetch_with_retry(url, params)

                poster_found = False
                if 'results' in data and len(data['results']) > 0:
                    result = data['results'][0]
                    poster_path = result.get('poster_path')

                    if poster_path:
                        poster_medium = f"https://image.tmdb.org/t/p/w500{poster_path}"
                        poster_large = f"https://image.tmdb.org/t/p/original{poster_path}"

                        # Validate poster URL before saving
                        if self._validate_poster_url(poster_medium):
                            movie['poster_url_medium'] = poster_medium
                            movie['poster_url_large'] = poster_large
                            movie['tmdb_id'] = result.get('id')
                            movie['tmdb_media_type'] = result.get('media_type')
                            enriched_count += 1
                            validated_count += 1
                            poster_found = True
                            print("✓ Poster added (validated)")
                        else:
                            print("✗ Poster URL invalid")

                # Fallback: Try TMDb find by IMDb ID if search failed
                if not poster_found and movie.get('imdb_id'):
                    try:
                        imdb_id = movie.get('imdb_id')
                        find_url = f"https://api.themoviedb.org/3/find/{imdb_id}"
                        find_params = {
                            'api_key': self.tmdb_api_key,
                            'external_source': 'imdb_id'
                        }

                        find_data = self._fetch_with_retry(find_url, find_params)

                        # Check movie results first, then TV results
                        results = find_data.get('movie_results', []) or find_data.get('tv_results', [])

                        if results and len(results) > 0:
                            result = results[0]
                            poster_path = result.get('poster_path')

                            if poster_path:
                                poster_medium = f"https://image.tmdb.org/t/p/w500{poster_path}"
                                poster_large = f"https://image.tmdb.org/t/p/original{poster_path}"

                                if self._validate_poster_url(poster_medium):
                                    movie['poster_url_medium'] = poster_medium
                                    movie['poster_url_large'] = poster_large
                                    movie['tmdb_id'] = result.get('id')
                                    movie['tmdb_media_type'] = 'movie' if 'movie_results' in find_data else 'tv'
                                    enriched_count += 1
                                    validated_count += 1
                                    imdb_fallback_count += 1
                                    poster_found = True
                                    print(f"✓ Poster added via IMDb ID (validated)")
                    except Exception as e:
                        pass  # Continue to print not found below

                if not poster_found:
                    if has_binged_poster:
                        binged_kept_count += 1
                        print("⊙ Using Binged poster (TMDb not found)")
                    else:
                        print("✗ No poster available")

                time.sleep(1.0)  # Rate limiting - increased from 0.3s

            except Exception as e:
                if has_binged_poster:
                    binged_kept_count += 1
                    print(f"⊙ Using Binged poster (TMDb error)")
                else:
                    print(f"✗ Error: {str(e)[:50]}")

        total_with_posters = enriched_count + binged_kept_count
        print(f"\n✅ Posters: {total_with_posters}/{len(self.movies)} movies")
        if enriched_count > 0:
            print(f"   ✓ {enriched_count} TMDb high-quality (validated)")
        if manual_count > 0:
            print(f"   📋 {manual_count} from manual corrections")
        if imdb_fallback_count > 0:
            print(f"   🔗 {imdb_fallback_count} via IMDb ID fallback")
        if binged_kept_count > 0:
            print(f"   ⊙ {binged_kept_count} using Binged fallback")
        self._save_json(self.movies, 'movies_with_tmdb.json')

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

        # Step 1: Scrape (includes Binged posters as fallback)
        await self.scrape_movies()

        # Test mode: limit to first 3 movies
        if self.test_mode and len(self.movies) > 3:
            print(f"\n🧪 TEST MODE: Processing only first 3 movies (out of {len(self.movies)})")
            self.movies = self.movies[:3]

        # Step 2: TMDb enrichment (upgrade posters + metadata)
        if self.movies:
            self.enrich_with_posters()

        # Step 3: YouTube trailers
        if self.movies:
            self.enrich_with_youtube()

        # Step 4: IMDb enrichment (fill missing data only)
        if self.movies:
            self.enrich_with_imdb()

        # Final: Save complete enriched data
        if self.movies:
            print("\n" + "="*60)
            print("SAVING FINAL ENRICHED DATA")
            print("="*60 + "\n")
            self._save_json(self.movies, 'movies_enriched.json')

        # Summary
        elapsed = time.time() - start_time

        # Count enrichments
        with_imdb = sum(1 for m in self.movies if m.get('imdb_id'))
        with_youtube = sum(1 for m in self.movies if m.get('youtube_id'))
        with_posters = sum(1 for m in self.movies if m.get('poster_url_large'))

        print("\n" + "="*60)
        print("✅ ALL DONE!")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"   • Movies scraped: {len(self.movies)}")
        print(f"   • With IMDb IDs: {with_imdb}/{len(self.movies)} {'✓' if with_imdb > 0 else '⊘ (optional)'}")
        print(f"   • With YouTube trailers: {with_youtube}/{len(self.movies)} {'✓' if with_youtube == len(self.movies) else '⚠'}")
        print(f"   • With TMDb posters: {with_posters}/{len(self.movies)} {'✓' if with_posters > len(self.movies)//2 else '⚠'}")
        print(f"   • Time elapsed: {elapsed:.1f} seconds")
        print(f"\n📁 Files created:")
        print(f"   • movies.json (scraped data)")
        if self.enable_posters:
            print(f"   • movies_with_tmdb.json (+ TMDb posters)")
        if self.enable_trailers:
            print(f"   • movies_with_trailers.json (+ YouTube)")
        print(f"   • movies_with_imdb.json (+ IMDb IDs)")
        print(f"   • movies_enriched.json (✨ FINAL - all data)")

        # Warnings/tips
        if with_posters < len(self.movies) // 2:
            print(f"\n💡 Tip: Set TMDB_API_KEY for high-quality posters")
            print(f"   Get free key: https://www.themoviedb.org/settings/api")

        if with_imdb < len(self.movies) // 4:
            print(f"\n⚠️  Note: IMDb enrichment low (Cinemagoer API may be down)")
            print(f"   This is optional - your site works without it!")

        print("\n" + "="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description='Unified movie scraper and enricher')
    parser.add_argument('--pages', type=int, default=5, help='Number of pages to scrape (default: 5)')
    parser.add_argument('--no-trailers', action='store_true', help='Skip YouTube trailer enrichment')
    parser.add_argument('--no-posters', action='store_true', help='Skip TMDb poster enrichment')
    parser.add_argument('--test', action='store_true', help='Test mode: process only 3 movies')

    args = parser.parse_args()

    updater = ContentUpdater(
        max_pages=args.pages,
        enable_trailers=not args.no_trailers,
        enable_posters=not args.no_posters,
        test_mode=args.test
    )

    asyncio.run(updater.run())


if __name__ == '__main__':
    main()
