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

# Optional: PIL for placeholder generation
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class ContentUpdater:
    """Unified content scraper and enricher with safety measures"""

    def __init__(self, max_pages=5, enable_posters=True, enable_trailers=True, test_mode=False, fetch_binged_posters=True, generate_placeholders=True):
        self.max_pages = max_pages
        self.enable_posters = enable_posters
        self.enable_trailers = enable_trailers
        self.test_mode = test_mode
        self.fetch_binged_posters = fetch_binged_posters
        self.generate_placeholders = generate_placeholders and PIL_AVAILABLE
        self.movies = []

        # IMDb client
        self.ia = Cinemagoer()

        # YouTube API (if available)
        self.youtube_api_key = os.environ.get('YOUTUBE_API_KEY')

        # TMDb API (if available)
        self.tmdb_api_key = os.environ.get('TMDB_API_KEY')

        # Load manual corrections
        self.manual_corrections = self._load_manual_corrections()

        # Platform mapping (ID from Binged.com image URLs to platform names)
        # Verified from actual website scraping
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

        # Platform color schemes for placeholder generation
        self.platform_colors = {
            'Netflix': ('#E50914', '#8B0000'),  # Red gradient
            'Amazon Prime Video': ('#00A8E1', '#00568B'),  # Blue gradient
            'Apple TV+': ('#000000', '#333333'),  # Black to dark gray
            'Jio Hotstar': ('#1F80E0', '#0F4070'),  # Blue gradient
            'Zee5': ('#9D34DA', '#6B1FA0'),  # Purple gradient
            'Sony LIV': ('#F47A20', '#C44500'),  # Orange gradient
            'Sun NXT': ('#FFD700', '#FFA500'),  # Gold to orange
            'Manorama MAX': ('#C41E3A', '#8B0000'),  # Red gradient
            'default': ('#1a1a1a', '#000000')  # Dark gradient
        }

        # Create placeholders directory if needed
        if self.generate_placeholders:
            os.makedirs('placeholders', exist_ok=True)

    async def scrape_movies(self):
        """Step 1: Scrape movies from Binged.com"""
        print("\n" + "="*60)
        print("STEP 1: SCRAPING MOVIES")
        print("="*60 + "\n")

        # URL for upcoming content (streaming-soon-month shows future releases)
        url = "https://www.binged.com/streaming-premiere-dates/?mode=streaming-soon-month&platform[]=Aha%20Video&platform[]=Amazon&platform[]=Apple%20Tv%20Plus&platform[]=Jio%20Hotstar&platform[]=Manorama%20MAX&platform[]=Netflix&platform[]=Sony%20LIV&platform[]=Sun%20NXT&platform[]=Zee5"

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

    async def enrich_with_binged_posters(self):
        """
        Step 1.5: Fetch high-quality posters directly from Binged content pages
        This is more reliable than extracting from the listing page
        """
        print("\n" + "="*60)
        print("STEP 1.5: FETCHING BINGED POSTERS FROM CONTENT PAGES")
        print("="*60 + "\n")

        # Filter movies that need poster enrichment
        movies_needing_posters = [m for m in self.movies if m.get('url') and not m.get('poster_url_binged')]

        if not movies_needing_posters:
            print("✅ All movies already have Binged posters from listing page")
            return

        print(f"📋 Fetching posters for {len(movies_needing_posters)} movies from detail pages...\n")

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

            posters_found = 0

            for i, movie in enumerate(movies_needing_posters, 1):
                title = movie.get('title', '')
                url = movie.get('url', '')

                print(f"[{i}/{len(movies_needing_posters)}] {title[:40]}... ", end='', flush=True)

                try:
                    # Navigate to the movie's detail page
                    await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                    await asyncio.sleep(1)  # Let page settle

                    # Wait for the poster image to load
                    try:
                        await page.wait_for_selector('img.movie-poster, img.show-poster, .movie-image img, .show-image img', timeout=5000)
                    except:
                        # Try alternative selectors
                        pass

                    # Get page content
                    content = await page.content()
                    soup = BeautifulSoup(content, 'html.parser')

                    # Try multiple selectors to find the poster image
                    poster_url = None

                    # Strategy 1: Look for specific poster classes
                    poster_selectors = [
                        'img.movie-poster',
                        'img.show-poster',
                        '.movie-image img',
                        '.show-image img',
                        '.movie-details img',
                        '.content-poster img',
                        'img[alt*="poster"]',
                        'img[alt*="Poster"]'
                    ]

                    for selector in poster_selectors:
                        img = soup.select_one(selector)
                        if img:
                            poster_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                            if poster_url:
                                break

                    # Strategy 2: Look for og:image meta tag
                    if not poster_url:
                        og_image = soup.find('meta', property='og:image')
                        if og_image:
                            poster_url = og_image.get('content')

                    # Strategy 3: Find largest image on the page (likely the poster)
                    if not poster_url:
                        all_imgs = soup.find_all('img')
                        for img in all_imgs:
                            src = img.get('src') or img.get('data-src')
                            if src and ('poster' in src.lower() or 'movie' in src.lower() or 'show' in src.lower()):
                                poster_url = src
                                break

                    if poster_url:
                        # Normalize the URL
                        if not poster_url.startswith('http'):
                            if poster_url.startswith('//'):
                                poster_url = 'https:' + poster_url
                            elif poster_url.startswith('/'):
                                poster_url = 'https://www.binged.com' + poster_url
                            else:
                                poster_url = 'https://www.binged.com/' + poster_url

                        # Skip placeholder images (Binged.png) and validate URL
                        if (poster_url.startswith('http') and
                            not poster_url.endswith('.svg') and
                            not poster_url.endswith('Binged.png') and
                            'Binged.png' not in poster_url):
                            # Only store as Binged fallback, don't set as primary poster
                            # TMDB will be prioritized in Step 2
                            movie['poster_url_binged'] = poster_url
                            posters_found += 1
                            print(f"✓ Poster found (Binged fallback)")
                        else:
                            print("⊙ Skipped (placeholder/invalid)")
                    else:
                        print("✗ No poster found")

                    # Rate limiting
                    await asyncio.sleep(0.5)

                except Exception as e:
                    print(f"✗ Error: {str(e)[:30]}")

            await browser.close()

        print(f"\n✅ Found {posters_found}/{len(movies_needing_posters)} posters from Binged content pages")
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

                    # Skip placeholder images (Binged.png) and validate URL
                    if (img_src.startswith('http') and
                        not img_src.endswith('.svg') and
                        not img_src.endswith('Binged.png') and
                        'Binged.png' not in img_src):
                        # Only store as Binged fallback, don't set as primary poster
                        movie_data['poster_url_binged'] = img_src

        return movie_data if movie_data.get('title') else None

    def enrich_with_imdb_fallback(self):
        """
        Step 3: IMDb Metadata Enrichment via Cinemagoer

        Two-phase approach:
        1. For movies WITH IMDb ID (from TMDB): Fetch metadata using IMDb ID directly
        2. For movies WITHOUT IMDb ID: Search by title to find IMDb ID + metadata

        This is more reliable than title-only search!
        """
        print("\n" + "="*60)
        print("STEP 3: IMDB METADATA ENRICHMENT (Cinemagoer)")
        print("="*60 + "\n")

        # Phase 1: Enrich movies that already have IMDb ID from TMDB
        with_imdb = [m for m in self.movies if m.get('imdb_id') and not m.get('imdb_year')]

        if with_imdb:
            print(f"📋 Phase 1: Fetching metadata for {len(with_imdb)} movies with IMDb IDs...\n")

            metadata_enriched = 0
            for i, movie in enumerate(with_imdb, 1):
                title = movie.get('title', '')
                imdb_id = movie.get('imdb_id', '')
                print(f"[{i}/{len(with_imdb)}] {title[:40]}... ", end='', flush=True)

                try:
                    # Extract numeric ID from tt1234567 format
                    movie_id = imdb_id.replace('tt', '')

                    # Fetch movie details using IMDb ID (more reliable!)
                    movie_info = self.ia.get_movie(movie_id)

                    if 'year' in movie_info:
                        movie['imdb_year'] = str(movie_info['year'])
                        metadata_enriched += 1
                        print(f"✓ Year: {movie['imdb_year']}")
                    else:
                        print("⊙ No year available")

                    time.sleep(0.5)  # Rate limiting

                except Exception as e:
                    print(f"✗ Error: {str(e)[:20]}")

            if metadata_enriched > 0:
                print(f"\n✅ Enriched {metadata_enriched}/{len(with_imdb)} movies with IMDb metadata\n")
        else:
            print("✅ All movies with IMDb IDs already have metadata\n")

        # Phase 2: Find IMDb IDs for movies that don't have them yet
        missing_imdb = [m for m in self.movies if not m.get('imdb_id')]

        if not missing_imdb:
            print("✅ All movies already have IMDb IDs from TMDB!")
            print("   Skipping search phase")
            self._save_json(self.movies, 'movies_with_imdb.json')
            return

        print(f"📋 Phase 2: Searching for {len(missing_imdb)} missing IMDb IDs...\n")

        search_found = 0
        for i, movie in enumerate(missing_imdb, 1):
            title = movie.get('title', '')
            print(f"[{i}/{len(missing_imdb)}] {title[:40]}... ", end='', flush=True)

            try:
                # Extract language for better search
                language = self._extract_language_from_url(movie.get('url', ''))
                search_query = f"{title} {language}" if language else title

                results = self.ia.search_movie(search_query)
                if results and len(results) > 0:
                    movie_id = results[0].movieID
                    movie['imdb_id'] = f"tt{movie_id}"

                    # Try to get year
                    try:
                        movie_info = self.ia.get_movie(movie_id)
                        if 'year' in movie_info:
                            movie['imdb_year'] = str(movie_info['year'])
                    except:
                        pass  # Year is optional

                    search_found += 1
                    year_info = f" ({movie.get('imdb_year', 'no year')})" if movie.get('imdb_year') else ""
                    print(f"✓ {movie['imdb_id']}{year_info}")
                else:
                    print("✗ Not found")

                time.sleep(0.5)  # Rate limiting

            except Exception as e:
                print(f"✗ Error: {str(e)[:20]}")

        if search_found > 0:
            print(f"\n✅ Found {search_found}/{len(missing_imdb)} IMDb IDs via title search")
        else:
            print(f"\n⚠️  Search phase: 0/{len(missing_imdb)} found (Cinemagoer API may be down)")
            print("   This is OK - TMDB already provided most IMDb IDs")

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

    def _get_imdb_from_tmdb(self, tmdb_id: int, media_type: str) -> Optional[str]:
        """
        Get IMDb ID from TMDB external_ids endpoint
        This is MORE RELIABLE than Cinemagoer API!
        """
        try:
            url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/external_ids"
            params = {'api_key': self.tmdb_api_key}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            imdb_id = data.get('imdb_id')

            # Validate IMDb ID format (tt + digits)
            if imdb_id and re.match(r'^tt\d{7,}$', imdb_id):
                return imdb_id

        except Exception as e:
            # Silent fail - not critical
            pass

        return None

    def _tmdb_search_query(self, query: str, year: Optional[str] = None) -> Optional[Dict]:
        """Execute TMDB search with given parameters"""
        try:
            url = "https://api.themoviedb.org/3/search/multi"
            params = {
                'api_key': self.tmdb_api_key,
                'query': query
            }
            if year:
                params['year'] = year

            data = self._fetch_with_retry(url, params)

            if data.get('results') and len(data['results']) > 0:
                return data['results'][0]
        except:
            pass

        return None

    def _search_tmdb(self, movie: Dict) -> Optional[Dict]:
        """
        Search TMDB with multiple fallback strategies
        Returns: First matching result or None
        """
        title = movie.get('title', '')
        year = movie.get('imdb_year', '')
        url = movie.get('url', '')

        # Extract language for better matching
        language = self._extract_language_from_url(url)
        clean_title = self._clean_title_for_search(title)

        # Strategy 1: Title + Language + Year
        search_query = f"{clean_title} {language}" if language else clean_title
        result = self._tmdb_search_query(search_query, year)
        if result:
            return result

        # Strategy 2: Title + Year (no language)
        if language:
            result = self._tmdb_search_query(clean_title, year)
            if result:
                return result

        # Strategy 3: Title only (no year, no language)
        if year:
            result = self._tmdb_search_query(clean_title, None)
            if result:
                return result

        return None

    def _wrap_text(self, text: str, max_width: int, font) -> List[str]:
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]

            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines if lines else [text]

    def generate_placeholder_poster(self, movie: Dict) -> Optional[str]:
        """
        Generate a beautiful placeholder poster using PIL/Pillow
        Returns the file path to the generated placeholder
        """
        if not PIL_AVAILABLE:
            return None

        try:
            title = movie.get('title', 'Untitled')
            platforms = movie.get('platforms', [])
            release_date = movie.get('release_date', '')

            # Choose primary platform for color scheme
            primary_platform = platforms[0] if platforms else 'default'
            colors = self.platform_colors.get(primary_platform, self.platform_colors['default'])

            # Image dimensions (standard poster size)
            width, height = 500, 750

            # Create image with gradient background
            img = Image.new('RGB', (width, height))
            draw = ImageDraw.Draw(img)

            # Draw gradient background
            for y in range(height):
                # Interpolate between the two colors
                ratio = y / height
                r1, g1, b1 = int(colors[0][1:3], 16), int(colors[0][3:5], 16), int(colors[0][5:7], 16)
                r2, g2, b2 = int(colors[1][1:3], 16), int(colors[1][3:5], 16), int(colors[1][5:7], 16)

                r = int(r1 + (r2 - r1) * ratio)
                g = int(g1 + (g2 - g1) * ratio)
                b = int(b1 + (b2 - b1) * ratio)

                draw.line([(0, y), (width, y)], fill=(r, g, b))

            # Try to load custom font, fall back to default
            try:
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
                subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
                platform_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
            except:
                # Fallback to default font
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
                platform_font = ImageFont.load_default()

            # Wrap title text
            max_title_width = width - 60  # 30px padding on each side
            title_lines = self._wrap_text(title, max_title_width, title_font)

            # Limit to 4 lines max
            if len(title_lines) > 4:
                title_lines = title_lines[:3] + [title_lines[3][:20] + '...']

            # Calculate total text height
            line_height = 45
            title_height = len(title_lines) * line_height

            # Draw title (centered vertically)
            y_offset = (height - title_height) // 2 - 50

            for line in title_lines:
                bbox = title_font.getbbox(line)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2

                # Draw text shadow
                draw.text((x + 2, y_offset + 2), line, fill=(0, 0, 0, 180), font=title_font)
                # Draw text
                draw.text((x, y_offset), line, fill=(255, 255, 255), font=title_font)
                y_offset += line_height

            # Draw release date
            if release_date:
                y_offset += 30
                bbox = subtitle_font.getbbox(release_date)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                draw.text((x + 1, y_offset + 1), release_date, fill=(0, 0, 0, 180), font=subtitle_font)
                draw.text((x, y_offset), release_date, fill=(200, 200, 200), font=subtitle_font)

            # Draw platform names
            if platforms:
                y_offset += 40
                platform_text = ' • '.join(platforms[:2])  # Max 2 platforms
                if len(platforms) > 2:
                    platform_text += f" +{len(platforms) - 2}"

                bbox = platform_font.getbbox(platform_text)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                draw.text((x + 1, y_offset + 1), platform_text, fill=(0, 0, 0, 180), font=platform_font)
                draw.text((x, y_offset), platform_text, fill=(180, 180, 180), font=platform_font)

            # Generate filename (sanitize title)
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-')).rstrip()
            safe_title = safe_title.replace(' ', '-').lower()[:50]

            # Save medium and large versions
            filename_medium = f"placeholders/{safe_title}-medium.jpg"
            filename_large = f"placeholders/{safe_title}-large.jpg"

            # Save medium (500x750)
            img.save(filename_medium, 'JPEG', quality=85, optimize=True)

            # Create larger version (1000x1500)
            img_large = img.resize((1000, 1500), Image.Resampling.LANCZOS)
            img_large.save(filename_large, 'JPEG', quality=90, optimize=True)

            return filename_medium

        except Exception as e:
            print(f"⚠️  Placeholder generation error: {str(e)[:50]}")
            return None

    def _apply_manual_correction(self, movie: Dict, title: str):
        """Apply manual correction data to movie"""
        correction = self.manual_corrections[title]
        if 'imdb_id' in correction:
            movie['imdb_id'] = correction['imdb_id']
        if 'imdb_year' in correction:
            movie['imdb_year'] = correction['imdb_year']
        if 'tmdb_id' in correction:
            movie['tmdb_id'] = correction['tmdb_id']
        if 'tmdb_media_type' in correction:
            movie['tmdb_media_type'] = correction['tmdb_media_type']

            # Fetch poster from TMDB if we have the ID (PRIORITY)
            try:
                tmdb_id = correction['tmdb_id']
                media_type = correction['tmdb_media_type']
                url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}"
                params = {'api_key': self.tmdb_api_key}

                data = self._fetch_with_retry(url, params)
                poster_path = data.get('poster_path')
                if poster_path:
                    movie['poster_url_medium'] = f"https://image.tmdb.org/t/p/w500{poster_path}"
                    movie['poster_url_large'] = f"https://image.tmdb.org/t/p/original{poster_path}"
                elif movie.get('poster_url_binged'):
                    # Fallback to Binged if TMDB doesn't have poster
                    movie['poster_url_medium'] = movie['poster_url_binged']
                    movie['poster_url_large'] = movie['poster_url_binged']

                backdrop_path = data.get('backdrop_path')
                if backdrop_path:
                    movie['backdrop_url'] = f"https://image.tmdb.org/t/p/original{backdrop_path}"
            except:
                # On error, fallback to Binged if available
                if movie.get('poster_url_binged'):
                    movie['poster_url_medium'] = movie['poster_url_binged']
                    movie['poster_url_large'] = movie['poster_url_binged']

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

    def enrich_with_tmdb(self):
        """
        Step 2: Complete TMDB Enrichment (TMDB-First Strategy)
        - Get TMDB ID via search
        - Extract IMDb ID from TMDB external_ids (more reliable than Cinemagoer!)
        - Get high-quality images (posters + backdrops)
        - Get metadata
        """
        if not self.enable_posters:
            print("\n⏭️  Skipping TMDB enrichment (disabled)")
            return

        if not self.tmdb_api_key:
            print("\n" + "="*60)
            print("⏭️  STEP 2: Skipping TMDB enrichment")
            print("="*60)
            print("\n💡 To enable TMDB enrichment:")
            print("   1. Get free API key: https://www.themoviedb.org/settings/api")
            print("   2. Set: export TMDB_API_KEY='your_key'")
            print("   3. Re-run this script")
            print("")
            return

        print("\n" + "="*60)
        print("STEP 2: TMDB COMPLETE ENRICHMENT (TMDB-FIRST STRATEGY)")
        print("="*60 + "\n")

        tmdb_found = 0
        imdb_from_tmdb = 0
        manual_count = 0
        binged_kept_count = 0

        for i, movie in enumerate(self.movies, 1):
            title = movie.get('title', '')
            has_binged_poster = bool(movie.get('poster_url_binged'))

            print(f"[{i}/{len(self.movies)}] {title[:40]}... ", end='', flush=True)

            # Check for manual correction first
            if title in self.manual_corrections:
                self._apply_manual_correction(movie, title)
                tmdb_found += 1
                manual_count += 1
                if movie.get('imdb_id'):
                    imdb_from_tmdb += 1
                print("✓ Manual correction applied")
                time.sleep(0.5)
                continue

            try:
                # 2a. Search TMDB by title + language
                tmdb_result = self._search_tmdb(movie)

                if tmdb_result:
                    tmdb_id = tmdb_result['id']
                    media_type = tmdb_result.get('media_type', 'movie')

                    # Store basic TMDB data
                    movie['tmdb_id'] = tmdb_id
                    movie['tmdb_media_type'] = media_type

                    # 2b. Get external IDs (including IMDb ID) ⭐
                    imdb_id = self._get_imdb_from_tmdb(tmdb_id, media_type)
                    if imdb_id:
                        movie['imdb_id'] = imdb_id
                        imdb_from_tmdb += 1

                    # 2c. Get high-quality posters from TMDB (PRIORITY)
                    poster_path = tmdb_result.get('poster_path')
                    if poster_path:
                        movie['poster_url_medium'] = f"https://image.tmdb.org/t/p/w500{poster_path}"
                        movie['poster_url_large'] = f"https://image.tmdb.org/t/p/original{poster_path}"
                    elif has_binged_poster:
                        # Fallback to Binged poster if TMDB doesn't have one
                        movie['poster_url_medium'] = movie['poster_url_binged']
                        movie['poster_url_large'] = movie['poster_url_binged']
                        binged_kept_count += 1

                    # 2d. Get backdrop (optional)
                    backdrop_path = tmdb_result.get('backdrop_path')
                    if backdrop_path:
                        movie['backdrop_url'] = f"https://image.tmdb.org/t/p/original{backdrop_path}"

                    tmdb_found += 1
                    status = "✓ TMDB + IMDb" if imdb_id else "✓ TMDB only"
                    print(status)
                else:
                    # TMDB not found, use Binged poster as fallback
                    if has_binged_poster:
                        movie['poster_url_medium'] = movie['poster_url_binged']
                        movie['poster_url_large'] = movie['poster_url_binged']
                        binged_kept_count += 1
                        print("⊙ Using Binged poster (TMDB not found)")
                    elif self.generate_placeholders:
                        # Generate placeholder poster
                        placeholder_path = self.generate_placeholder_poster(movie)
                        if placeholder_path:
                            movie['poster_url_medium'] = placeholder_path
                            movie['poster_url_large'] = placeholder_path.replace('-medium.jpg', '-large.jpg')
                            movie['poster_generated'] = True
                            print("✓ Generated placeholder poster")
                        else:
                            print("✗ No poster available")
                    else:
                        print("✗ No poster available")

                time.sleep(0.5)  # Rate limiting

            except Exception as e:
                # On error, fallback to Binged poster if available
                if has_binged_poster:
                    movie['poster_url_medium'] = movie['poster_url_binged']
                    movie['poster_url_large'] = movie['poster_url_binged']
                    binged_kept_count += 1
                    print(f"⊙ Using Binged poster (TMDB error)")
                elif self.generate_placeholders:
                    # Generate placeholder poster
                    placeholder_path = self.generate_placeholder_poster(movie)
                    if placeholder_path:
                        movie['poster_url_medium'] = placeholder_path
                        movie['poster_url_large'] = placeholder_path.replace('-medium.jpg', '-large.jpg')
                        movie['poster_generated'] = True
                        print("✓ Generated placeholder (TMDB error)")
                    else:
                        print(f"✗ Error: {str(e)[:30]}")
                else:
                    print(f"✗ Error: {str(e)[:30]}")

        # Count placeholders generated
        placeholders_generated = sum(1 for m in self.movies if m.get('poster_generated'))

        total_with_posters = tmdb_found + binged_kept_count + placeholders_generated
        print(f"\n✅ TMDB enrichment: {tmdb_found}/{len(self.movies)} movies")
        print(f"   🎬 TMDB IDs found: {tmdb_found}/{len(self.movies)}")
        print(f"   🎭 IMDb IDs from TMDB: {imdb_from_tmdb}/{len(self.movies)}")
        if manual_count > 0:
            print(f"   📋 Manual corrections: {manual_count}")
        if binged_kept_count > 0:
            print(f"   ⊙ Binged fallback posters: {binged_kept_count}")
        if placeholders_generated > 0:
            print(f"   🎨 Generated placeholders: {placeholders_generated}")
        print(f"   📸 Total with posters: {total_with_posters}/{len(self.movies)}")
        self._save_json(self.movies, 'movies_with_tmdb.json')

    def _save_json(self, data, filename):
        """Save data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved: {filename}")

    async def run(self):
        """Run all steps with TMDB-First strategy"""
        start_time = time.time()

        print("\n" + "="*60)
        print("UNIFIED CONTENT UPDATER (TMDB-FIRST STRATEGY)")
        print("="*60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

        # Step 1: Scrape from Binged (includes Binged posters as fallback)
        await self.scrape_movies()

        # Test mode: limit to first 3 movies
        if self.test_mode and len(self.movies) > 3:
            print(f"\n🧪 TEST MODE: Processing only first 3 movies (out of {len(self.movies)})")
            self.movies = self.movies[:3]

        # Step 1.5: Fetch missing Binged posters from content pages
        if self.movies and self.fetch_binged_posters:
            await self.enrich_with_binged_posters()

        # Step 2: TMDB Complete Enrichment (TMDB ID + IMDb ID + Images) ⭐
        if self.movies and self.enable_posters:
            self.enrich_with_tmdb()

        # Step 3: Cinemagoer Fallback (only for missing IMDb IDs)
        if self.movies:
            self.enrich_with_imdb_fallback()

        # Step 4: YouTube Trailers
        if self.movies and self.enable_trailers:
            self.enrich_with_youtube()

        # Final: Save complete enriched data
        if self.movies:
            print("\n" + "="*60)
            print("SAVING FINAL ENRICHED DATA")
            print("="*60 + "\n")
            self._save_json(self.movies, 'movies_enriched.json')

        # Summary
        elapsed = time.time() - start_time

        # Count enrichments
        with_tmdb = sum(1 for m in self.movies if m.get('tmdb_id'))
        with_imdb = sum(1 for m in self.movies if m.get('imdb_id'))
        with_youtube = sum(1 for m in self.movies if m.get('youtube_id'))
        with_posters = sum(1 for m in self.movies if m.get('poster_url_large'))

        print("\n" + "="*60)
        print("✅ ALL DONE!")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"   • Movies scraped: {len(self.movies)}")
        print(f"   • With TMDB IDs: {with_tmdb}/{len(self.movies)} {'✓' if with_tmdb > len(self.movies)//2 else '⚠'}")
        print(f"   • With IMDb IDs: {with_imdb}/{len(self.movies)} {'✓' if with_imdb > len(self.movies)//2 else '⚠'}")
        print(f"   • With high-quality posters: {with_posters}/{len(self.movies)} {'✓' if with_posters > len(self.movies)//2 else '⚠'}")
        print(f"   • With YouTube trailers: {with_youtube}/{len(self.movies)} {'✓' if with_youtube > 0 else '⊘'}")
        print(f"   • Time elapsed: {elapsed:.1f} seconds")
        print(f"\n📁 Files created:")
        print(f"   • movies.json (scraped data)")
        if self.enable_posters:
            print(f"   • movies_with_tmdb.json (+ TMDB enrichment)")
        print(f"   • movies_with_imdb.json (+ IMDb fallback)")
        if self.enable_trailers:
            print(f"   • movies_with_trailers.json (+ YouTube)")
        print(f"   • movies_enriched.json (✨ FINAL - all data)")

        # Warnings/tips
        if with_tmdb < len(self.movies) // 2:
            print(f"\n💡 Tip: Set TMDB_API_KEY for better enrichment")
            print(f"   Get free key: https://www.themoviedb.org/settings/api")

        if with_imdb > len(self.movies) * 0.8:
            print(f"\n🎉 Great! {with_imdb}/{len(self.movies)} movies have IMDb IDs")
            print(f"   TMDB-first strategy is working well!")

        print("\n" + "="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description='Unified movie scraper and enricher')
    parser.add_argument('--pages', type=int, default=5, help='Number of pages to scrape (default: 5)')
    parser.add_argument('--no-trailers', action='store_true', help='Skip YouTube trailer enrichment')
    parser.add_argument('--no-posters', action='store_true', help='Skip TMDb poster enrichment')
    parser.add_argument('--no-binged-posters', action='store_true', help='Skip fetching posters from Binged content pages')
    parser.add_argument('--no-placeholders', action='store_true', help='Skip generating placeholder posters (requires Pillow)')
    parser.add_argument('--test', action='store_true', help='Test mode: process only 3 movies')

    args = parser.parse_args()

    # Check if Pillow is needed but not available
    if not args.no_placeholders and not PIL_AVAILABLE:
        print("⚠️  Pillow not available. Placeholder generation will be disabled.")
        print("💡 Install with: pip3 install pillow")

    updater = ContentUpdater(
        max_pages=args.pages,
        enable_trailers=not args.no_trailers,
        enable_posters=not args.no_posters,
        fetch_binged_posters=not args.no_binged_posters,
        generate_placeholders=not args.no_placeholders,
        test_mode=args.test
    )

    asyncio.run(updater.run())


if __name__ == '__main__':
    main()
